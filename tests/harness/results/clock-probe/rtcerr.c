/* rtcerr -- how often, and when, does a CMOS RTC register read come back
   wrong on this machine? Read-only. */
#include <stdio.h>
#include <time.h>
#include <pc.h>
static int rd(int reg){ outportb(0x70, reg & 0x7F); return inportb(0x71); }
static int rd_delay(int reg){ outportb(0x70, reg & 0x7F); outportb(0x80,0); outportb(0x80,0); return inportb(0x71); }
int main(void){
  setvbuf(stdout,NULL,_IONBF,0);
  uclock();
  /* 1. reg B is constant: any value other than the mode is a misread */
  { long n=0,bad=0,uip_bad=0; int mode=rd(0x0B), first_bad=-1; uclock_t t0=uclock();
    while(uclock()-t0 < (uclock_t)UCLOCKS_PER_SEC*6){ int a=rd(0x0A); int b=rd(0x0B); n++; if(b!=mode){ bad++; if(first_bad<0) first_bad=b; if(a&0x80) uip_bad++; } }
    printf("1_regB_plain   reads=%ld bad=%ld (of which UIP set at the time=%ld) mode=%02x first_bad=%02x\n",n,bad,uip_bad,mode,first_bad&0xff); }
  { long n=0,bad=0; int mode=rd_delay(0x0B), first_bad=-1; uclock_t t0=uclock();
    while(uclock()-t0 < (uclock_t)UCLOCKS_PER_SEC*6){ int b=rd_delay(0x0B); n++; if(b!=mode){ bad++; if(first_bad<0) first_bad=b; } }
    printf("2_regB_iodelay reads=%ld bad=%ld mode=%02x first_bad=%02x\n",n,bad,mode,first_bad&0xff); }
  /* 3. hours is constant over this test (unless run across an hour edge): misreads, split by UIP state and by time since the last seconds edge */
  { long n=0,bad=0,bad_uip=0,bad_first5ms=0; int hr=rd(0x04), s_prev=rd(0x00), first_bad=-1; uclock_t t0=uclock(), edge=t0;
    while(uclock()-t0 < (uclock_t)UCLOCKS_PER_SEC*8){
      int a=rd(0x0A); int s=rd(0x00); int h=rd(0x04); uclock_t t=uclock(); n++;
      if(s!=s_prev){ s_prev=s; edge=t; }
      if(h!=hr){ bad++; if(first_bad<0) first_bad=h; if(a&0x80) bad_uip++; if(t-edge < (uclock_t)UCLOCKS_PER_SEC/200) bad_first5ms++; } }
    printf("3_hours        reads=%ld bad=%ld bad_with_UIP=%ld bad_within_5ms_after_edge=%ld hr=%02x first_bad=%02x\n",n,bad,bad_uip,bad_first5ms,hr,first_bad&0xff); }
  /* 4. what does the seconds register read while UIP is set? */
  { long n=0,uip=0,odd=0; int s_prev=rd(0x00); uclock_t t0=uclock();
    while(uclock()-t0 < (uclock_t)UCLOCKS_PER_SEC*6){ int a=rd(0x0A); int s=rd(0x00); n++; if(a&0x80){ uip++; if(s!=s_prev && s!=((s_prev&0x0f)==9? ((s_prev&0xf0)+0x10)%0x60 : s_prev+1)) odd++; } else s_prev=s; }
    printf("4_uip          reads=%ld uip_set=%ld odd_seconds_during_uip=%ld\n",n,uip,odd); }
  return 0; }
