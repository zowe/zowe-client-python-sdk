//JOBNAME2 JOB (ACCT),&SYSUID,                     
//            CLASS=A,MSGCLASS=X,NOTIFY=&SYSUID                                               
/*JOBPARM S=ZOS1                                    
//*--------------------------------------------         
//*- DO NOTHING, JUST WAIT 5 SECONDS ---------         
//*--------------------------------------------         
//STEP1 EXEC PGM=BPXBATCH,PARM='sh sleep 05'            