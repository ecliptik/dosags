#include <stdio.h>
#include <string.h>
#include <time.h>
#include <dos.h>
#include <dpmi.h>
#include <pc.h>
static int cmos(int reg) { outportb(0x70, reg & 0x7F); return inportb(0x71); }
int main(void){
  struct date d; struct time t; __dpmi_regs r; time_t now;
  setvbuf(stdout,NULL,_IONBF,0);
  getdate(&d); gettime(&t);
  printf("dos_date=%04d-%02d-%02d dos_time=%02d:%02d:%02d\n", d.da_year, d.da_mon, d.da_day, t.ti_hour, t.ti_min, t.ti_sec);
  printf("rtc: sec=%02x min=%02x hr=%02x dow=%02x day=%02x mon=%02x yr=%02x cent32=%02x cent37=%02x regA=%02x regB=%02x regD=%02x\n",
    cmos(0),cmos(2),cmos(4),cmos(6),cmos(7),cmos(8),cmos(9),cmos(0x32),cmos(0x37),cmos(0x0A),cmos(0x0B),cmos(0x0D));
  memset(&r,0,sizeof r); r.h.ah=4; __dpmi_int(0x1a,&r);
  printf("int1a_04 flags=%04x cx=%04x dx=%04x\n", r.x.flags, r.x.cx, r.x.dx);
  memset(&r,0,sizeof r); r.h.ah=0; __dpmi_int(0x1a,&r);
  printf("int1a_00 ticks=%04x%04x midnight_flag=%02x\n", r.x.cx, r.x.dx, r.h.al);
  now=time(0); printf("time()=%ld %s", (long)now, ctime(&now));
  printf("TZ=%s\n", getenv("TZ") ? getenv("TZ") : "(unset)");
  return 0;
}
