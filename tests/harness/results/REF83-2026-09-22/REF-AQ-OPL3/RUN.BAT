@ECHO OFF
SET BLASTER=A220 I5 D1 H5 T6
SET DOSAGS_FIXED_TIMESTEP=1
AGS.EXE --test --log-stdout=+mgs:all --user-data-dir c:\  > STDOUT.TXT
