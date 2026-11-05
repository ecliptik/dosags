// mkroom -- apply a room description (XML) to an AGS room file.
//
// License: MIT (dosags's own tooling, see LICENSE in the repo root).
//
// AGS 3.6.3's headless tools cover a room's IMAGES and SCRIPT (crmpak)
// but not its DATA: hotspot names and event handlers, object placements,
// walkable-area properties, walk-behind baselines, edges. Those live in
// the room file's main block, which only Common/game/room_file.cpp's
// WriteRoomData() writes. This tool reads a room crmpak created, sets
// exactly the fields below from an XML description, and writes it back
// through that same WriteRoomData() -- no format code of our own.
//
// Each field cites where the pinned engine's writer puts it
// (Common/game/room_file.cpp, WriteMainBlock(), v3.6.3.13):
//   Width/Height/MaskResolution          :988-992
//   Edges                                :954-957
//   Hotspots[i].WalkTo/Name/ScriptName   :941-950
//   Hotspots[i].EventHandlers            :971-975
//   Objects (WriteRoomObject)            :959-963, names in the ObjNames
//                                         and ObjectScNames ext blocks
//   Objects[i].Baseline / Flags          :986-991
//   Objects[i].EventHandlers             :976-979
//   WalkAreas[i].ScalingFar/Near/...     :994-1004
//   WalkBehinds[i].Baseline              :937-939
//   room EventHandlers                   :969-970
//   GameID                               :1015
//
// Usage: mkroom <in.crm> <room.xml> <out.crm>
// XML (TinyXML2 is already part of AGS's libtools, so no new dependency;
// PLAN.md said JSON -- XML avoids carrying a JSON parser for ~60 lines of
// input):
//   <Room Width="320" Height="200" MaskResolution="1" GameID="123">
//     <Edges Left="0" Right="319" Top="40" Bottom="199"/>
//     <Event Index="7" Function="room_AfterFadeIn"/>
//     <Hotspot ID="1" Name="Sign" ScriptName="hSign" WalkToX="0" WalkToY="0">
//       <Event Index="1" Function="hSign_Look"/>
//     </Hotspot>
//     <Object Name="Key" ScriptName="oKey" X="200" Y="150" Sprite="7"
//             Visible="1" Baseline="0" Clickable="1">
//       <Event Index="1" Function="oKey_Interact"/>
//     </Object>
//     <WalkArea ID="1" ScalingFar="100" ScalingNear="100"/>
//     <WalkBehind ID="1" Baseline="150"/>
//   </Room>
// Event indices are the engine's own (Engine/ac/event.h kRoomEvent_*,
// Engine/ac/global_hotspot.cpp:106-113, Engine/ac/global_object.cpp:453-459).

#include <cstdio>
#include <cstdlib>
#include <memory>
#include <string>
#include <tinyxml2.h>
#include "game/room_file.h"
#include "game/roomdata.h"
#include "game/interactions.h"
#include "util/file.h"
#include "util/stream.h"
#include "util/string.h"

using namespace AGS::Common;
using tinyxml2::XMLElement;

// Flags from Common/ac/common_defines.h (OBJF_*), kept local and minimal.
static const int kObjfNoInteract = 0x01; // OBJF_NOINTERACT

static std::unique_ptr<InteractionEvents> ReadEvents(const XMLElement *parent, size_t min_count)
{
    std::unique_ptr<InteractionEvents> evts(new InteractionEvents());
    size_t count = min_count;
    for (const XMLElement *e = parent->FirstChildElement("Event"); e; e = e->NextSiblingElement("Event"))
    {
        const int idx = e->IntAttribute("Index", -1);
        if (idx >= 0 && static_cast<size_t>(idx + 1) > count)
            count = idx + 1;
    }
    for (size_t i = 0; i < count; ++i)
        evts->Events.push_back(InteractionEvents::EventHandler(String()));
    for (const XMLElement *e = parent->FirstChildElement("Event"); e; e = e->NextSiblingElement("Event"))
    {
        const int idx = e->IntAttribute("Index", -1);
        const char *fn = e->Attribute("Function");
        if (idx < 0 || !fn)
            continue;
        evts->Events[idx] = InteractionEvents::EventHandler(String(fn));
    }
    return evts;
}

int main(int argc, char *argv[])
{
    if (argc < 4)
    {
        std::printf("Usage: mkroom <in.crm> <room.xml> <out.crm>\n");
        return 2;
    }
    const char *in_crm = argv[1], *in_xml = argv[2], *out_crm = argv[3];

    RoomDataExt room;
    {
        RoomDataSource src;
        HRoomFileError err = OpenRoomFile(String(in_crm), src);
        if (!err)
        {
            std::printf("mkroom: cannot open %s: %s\n", in_crm, err->FullMessage().GetCStr());
            return 1;
        }
        err = ReadRoomData(&room, std::move(src.InputStream), src.DataVersion);
        if (!err)
        {
            std::printf("mkroom: cannot read %s: %s\n", in_crm, err->FullMessage().GetCStr());
            return 1;
        }
    }

    tinyxml2::XMLDocument doc;
    if (doc.LoadFile(in_xml) != tinyxml2::XML_SUCCESS)
    {
        std::printf("mkroom: cannot parse %s: %s\n", in_xml, doc.ErrorStr());
        return 1;
    }
    const XMLElement *r = doc.FirstChildElement("Room");
    if (!r)
    {
        std::printf("mkroom: %s has no <Room> root\n", in_xml);
        return 1;
    }

    room.Width = r->IntAttribute("Width", room.Width);
    room.Height = r->IntAttribute("Height", room.Height);
    room.MaskResolution = r->IntAttribute("MaskResolution", room.MaskResolution);
    room.GameID = r->IntAttribute("GameID", room.GameID);

    if (const XMLElement *e = r->FirstChildElement("Edges"))
        room.Edges = RoomEdges(e->IntAttribute("Left", 0), e->IntAttribute("Right", room.Width - 1),
                               e->IntAttribute("Top", 0), e->IntAttribute("Bottom", room.Height - 1));

    // Room events: 10 slots, Engine/ac/event.h kRoomEvent_EdgeLeft..AfterFadeout.
    room.EventHandlers = ReadEvents(r, 10);

    // Hotspots. Hotspot 0 is "no hotspot"; counts are highest ID + 1.
    uint32_t hot_count = 1;
    for (const XMLElement *e = r->FirstChildElement("Hotspot"); e; e = e->NextSiblingElement("Hotspot"))
    {
        const int id = e->IntAttribute("ID", -1);
        if (id < 0 || id >= MAX_ROOM_HOTSPOTS)
        {
            std::printf("mkroom: hotspot ID %d out of range\n", id);
            return 1;
        }
        RoomHotspot &h = room.Hotspots[id];
        h.Name = e->Attribute("Name") ? e->Attribute("Name") : "";
        h.ScriptName = e->Attribute("ScriptName") ? e->Attribute("ScriptName") : "";
        h.WalkTo = Point(e->IntAttribute("WalkToX", 0), e->IntAttribute("WalkToY", 0));
        h.EventHandlers = ReadEvents(e, 10);
        if (static_cast<uint32_t>(id + 1) > hot_count)
            hot_count = id + 1;
    }
    room.HotspotCount = hot_count;

    // Objects, in document order (their index is their ID).
    room.Objects.clear();
    for (const XMLElement *e = r->FirstChildElement("Object"); e; e = e->NextSiblingElement("Object"))
    {
        RoomObjectInfo o;
        o.Name = e->Attribute("Name") ? e->Attribute("Name") : "";
        o.ScriptName = e->Attribute("ScriptName") ? e->Attribute("ScriptName") : "";
        o.X = e->IntAttribute("X", 0);
        o.Y = e->IntAttribute("Y", 0);
        o.Sprite = e->IntAttribute("Sprite", 0);
        o.IsOn = e->IntAttribute("Visible", 1) != 0;
        o.Baseline = e->IntAttribute("Baseline", 0); // 0 = follow Y
        o.Flags = e->IntAttribute("Clickable", 1) != 0 ? 0 : kObjfNoInteract;
        o.EventHandlers = ReadEvents(e, 8);
        room.Objects.push_back(std::move(o));
    }

    uint32_t wa_count = 1;
    for (const XMLElement *e = r->FirstChildElement("WalkArea"); e; e = e->NextSiblingElement("WalkArea"))
    {
        const int id = e->IntAttribute("ID", -1);
        if (id < 0 || id >= MAX_WALK_AREAS)
        {
            std::printf("mkroom: walkable area ID %d out of range\n", id);
            return 1;
        }
        WalkArea &wa = room.WalkAreas[id];
        // The file stores scaling as (percent - 100); see how
        // Engine/ac/walkablearea.cpp adds 100 back when it reads them.
        wa.ScalingFar = e->IntAttribute("ScalingFar", 100) - 100;
        wa.ScalingNear = e->IntAttribute("ScalingNear", 100) - 100;
        if (static_cast<uint32_t>(id + 1) > wa_count)
            wa_count = id + 1;
    }
    room.WalkAreaCount = wa_count;

    uint32_t wb_count = 1;
    for (const XMLElement *e = r->FirstChildElement("WalkBehind"); e; e = e->NextSiblingElement("WalkBehind"))
    {
        const int id = e->IntAttribute("ID", -1);
        if (id < 0 || id >= MAX_WALK_BEHINDS)
        {
            std::printf("mkroom: walk-behind ID %d out of range\n", id);
            return 1;
        }
        room.WalkBehinds[id].Baseline = e->IntAttribute("Baseline", 0);
        if (static_cast<uint32_t>(id + 1) > wb_count)
            wb_count = id + 1;
    }
    room.WalkBehindCount = wb_count;

    std::unique_ptr<Stream> out = File::CreateFile(String(out_crm));
    if (!out)
    {
        std::printf("mkroom: cannot create %s\n", out_crm);
        return 1;
    }
    HRoomFileError werr = WriteRoomData(&room, out.get(), kRoomVersion_Current);
    if (!werr)
    {
        std::printf("mkroom: cannot write %s: %s\n", out_crm, werr->FullMessage().GetCStr());
        return 1;
    }
    std::printf("mkroom: %s -> %s (%u hotspots, %u objects, %u walkable areas, %u walk-behinds)\n",
                in_crm, out_crm, room.HotspotCount, (unsigned)room.Objects.size(),
                room.WalkAreaCount, room.WalkBehindCount);
    return 0;
}
