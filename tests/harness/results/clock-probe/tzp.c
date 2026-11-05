#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <errno.h>
#include <fcntl.h>
#include <unistd.h>
#include <time.h>
#include <sys/time.h>
#include <sys/stat.h>
static void show(const char *tag){
  time_t now=time(0); struct tm lt=*localtime(&now); struct timeval tv; uclock_t t0; int i; char buf[64];
  strftime(buf,sizeof buf,"%Y-%m-%dT%H:%M:%SZ",gmtime(&now));
  t0=uclock(); for(i=0;i<100;i++) gettimeofday(&tv,0);
  printf("%-22s time()=%lu gmtime=%s local=%02d:%02d:%02d gmtoff=%ld zone=%s gettimeofday_us=%.1f\n", tag,(unsigned long)now,buf,lt.tm_hour,lt.tm_min,lt.tm_sec,(long)lt.tm_gmtoff,lt.tm_zone?lt.tm_zone:"(null)",(double)(uclock()-t0)*1e6/UCLOCKS_PER_SEC/100);
}
static void tryopen(const char *p){
  char fixed[512]; int fd; struct stat st; extern void _fixpath(const char *, char *);
  _fixpath(p, fixed);
  errno=0; fd=open(p,O_RDONLY|O_BINARY);
  if(fd<0){ printf("open(%s) -> FAILED errno=%d fixpath=%s\n",p,errno,fixed); return; }
  if(fstat(fd,&st)==0) printf("open(%s) -> OK size=%ld fixpath=%s\n",p,(long)st.st_size,fixed); else printf("open(%s) -> OK fstat failed fixpath=%s\n",p,fixed);
  { unsigned char b[48]; int n=read(fd,b,sizeof b), i; printf("  first %d bytes:",n); for(i=0;i<n;i++) printf(" %02x",b[i]); printf("\n"); }
  close(fd);
}
int main(void){
  setvbuf(stdout,NULL,_IONBF,0); uclock();
  printf("TZ=%s TZDIR=%s DJDIR=%s DJGPP=%s\n", getenv("TZ")?getenv("TZ"):"(unset)", getenv("TZDIR")?getenv("TZDIR"):"(unset)", getenv("DJDIR")?getenv("DJDIR"):"(unset)", getenv("DJGPP")?getenv("DJGPP"):"(unset)");
  show("1_default");
  tryopen("/dev/env/DJDIR/etc/localtime");
  tryopen("/etc/localtime");
  tryopen("/dev/env/DJDIR/zoneinfo/localtime");
  tryopen("/dev/env/DJDIR/zoneinfo/posixrules");
  tryopen("/dev/env/DJDIR/zoneinfo/GMT");
  setenv("TZ","UTC0",1); tzset(); show("2_TZ=UTC0");
  setenv("TZ","",1); tzset(); show("3_TZ=empty");
  unsetenv("TZ"); tzset(); show("4_TZ_unset_again");
  return 0; }
