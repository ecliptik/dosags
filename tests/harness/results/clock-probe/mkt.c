#include <stdio.h>
#include <string.h>
#include <time.h>
static double cost(int year, int n){
  struct tm t; uclock_t t0; int i; volatile long s=0; time_t r=0;
  t0=uclock();
  for(i=0;i<n;i++){ memset(&t,0,sizeof t); t.tm_year=year-1900; t.tm_mon=3; t.tm_mday=13; t.tm_hour=13; t.tm_min=34; t.tm_sec=12; t.tm_isdst=-1; r=mktime(&t); s+=r; }
  printf("year=%d mktime_us=%.1f result=%ld\n", year, (double)(uclock()-t0)*1e6/UCLOCKS_PER_SEC/n, (long)r);
  return 0;
}
int main(void){ int y[]={1990,2026,2037,2038,2039,2059,2071,2100}; int i; setvbuf(stdout,NULL,_IONBF,0); uclock(); for(i=0;i<8;i++) cost(y[i],200); return 0; }
