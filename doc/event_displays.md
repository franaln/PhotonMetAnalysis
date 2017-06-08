Instructions to get the event displays (June 2017)
--------------------------------------------------

Using lxplus:

mkdir ~/AtlasProduction-20.7.7.2/
cd ~/AtlasProduction-20.7.7.2/

setupATLAS
asetup 20.7.7.2,gcc49,opt,here,AtlasProduction

cp /afs/cern.ch/atlas/project/Atlantis/Tutorial/packageUpdateJiveXML_Jun15.sh .
source packageUpdateJiveXML_Jun15.sh


lsetup panda
voms-proxy-init -voms atlas


pathena JiveXML_jobOptions_PhysicsRAW_run2_2016.py \
    --eventPickEvtList events.txt \
    --eventPickDataType RAW \
    --eventPickStreamName physics_Main \
    --outDS user.falonso.AtlantisData2017Analysis \
    --supStream GLOBAL --extOutFile JiveXML*.xml

where events.txt contains all the runs/events like this:

00279169 1520974298
00302347 1213250725
00303338 5281158915
00303846 2905102101
00304008 1606290537
00304243 2585959042
00307935 1355394550
00310872 1451070076
00300863 1305667903
00304008 1673324753
00311365 1079519224
