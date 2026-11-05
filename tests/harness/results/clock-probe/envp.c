#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <time.h>
#include <sys/time.h>
#include <dos.h>
extern char **environ;
int main(int argc, char **argv){
  int i; struct date d; struct time t; time_t now; struct timeval tv; uclock_t t0; char buf[64]; struct tm *g; struct tm lt;
  setvbuf(stdout,NULL,_IONBF,0);
  for(i=0; environ[i]; i++) printf("env[%d]=%s\n", i, environ[i]);
  getdate(&d); gettime(&t);
  printf("dos_date=%04d-%02d-%02d dos_time=%02d:%02d:%02d\n", d.da_year, d.da_mon, d.da_day, t.ti_hour, t.ti_min, t.ti_sec);
  now=time(0); g=gmtime(&now); strftime(buf,sizeof buf,"%Y-%m-%dT%H:%M:%SZ",g);
  printf("time()=%lu gmtime=%s\n",(unsigned long)now,buf);
  lt=*localtime(&now); printf("localtime=%04d-%02d-%02d %02d:%02d:%02d isdst=%d gmtoff=%ld zone=%s tzname=%s/%s\n", lt.tm_year+1900, lt.tm_mon+1, lt.tm_mday, lt.tm_hour, lt.tm_min, lt.tm_sec, lt.tm_isdst, (long)lt.tm_gmtoff, lt.tm_zone?lt.tm_zone:"(null)", tzname[0], tzname[1]);
  uclock(); t0=uclock(); for(i=0;i<100;i++) gettimeofday(&tv,0);
  printf("gettimeofday_us=%.1f\n",(double)(uclock()-t0)*1e6/UCLOCKS_PER_SEC/100);
  return 0; }
