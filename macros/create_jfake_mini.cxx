#include <TROOT.h>
#include <TChain.h>
#include <TFile.h>
#include <TH1F.h>
#include <TTreeReader.h>
#include <TTreeReaderValue.h>
#include <TTreeReaderArray.h>
#include <TMath.h>

#include <vector>
#include <iostream>

//#define EXTRA_VARS

float get_dphi(float phi1, float phi2)
{
  float  phi = fabs(phi1 - phi2);
  if(phi <= TMath::Pi())  return phi;
  else                    return (2 * TMath::Pi() - phi);
}

float fjg_factor[2*3] = {
  0.147, 0.133, 0.124, // eta < 1.37:  145<pt<175, 175<pt<225, pt>225
  0.100, 0.096, 0.104  // eta > 1.52:  145<pt<175, 175<pt<225, pt>225
};

unsigned int get_eta_bin(float eta)
{
  float abseta = fabs(eta);

  if (abseta < 1.37)
    return 0;
  else if (abseta > 1.52 && abseta <= 2.37)
    return 1;

  return 99;
}

unsigned int get_pt_bin(float pt)
{
  if (pt > 145. && pt <= 175.)
    return 0;
  else if (pt > 175. && pt <= 225.)
    return 1;
  else if (pt > 225.)
    return 2;

  return 99;
}

  
void loop(TString input_path, TString output_path)
{
  // open the file
  TFile *f = TFile::Open(input_path);
  if (f == 0) {
    // if we cannot open the file, print an error message and return immediatly
    printf("Error: cannot open input file\n");
    return;
  }
  
  TTreeReader reader("mini", f); 

  Int_t total_events = reader.GetEntries(true);
  
  if (total_events == 0) {
    std::cout << "no events" << std::endl;
    return;
  }

  std::cout << "create_jfake_mini: " << input_path << " -> " << output_path << std::endl;

  TTreeReaderValue<int> event(reader, "event");
  TTreeReaderValue<float> avgmu(reader, "avgmu");

  TTreeReaderValue<float> weight_mc(reader, "weight_mc");
  TTreeReaderValue<float> weight_pu(reader, "weight_pu");
  TTreeReaderValue<float> weight_sf(reader, "weight_sf");

  TTreeReaderValue<int> ph_n(reader, "ph_n");
  TTreeReaderValue< std::vector<float> > ph_pt(reader, "ph_pt");
  TTreeReaderValue< std::vector<float> > ph_eta(reader, "ph_eta");
  TTreeReaderValue< std::vector<float> > ph_phi(reader, "ph_phi");
  TTreeReaderValue< std::vector<float> > ph_iso(reader, "ph_iso");
  TTreeReaderValue< std::vector<float> > ph_w(reader, "ph_w");

  TTreeReaderValue<int> ph_noniso_n(reader, "ph_noniso_n");
  TTreeReaderValue< std::vector<float> > ph_noniso_pt(reader, "ph_noniso_pt");
  TTreeReaderValue< std::vector<float> > ph_noniso_eta(reader, "ph_noniso_eta");
  TTreeReaderValue< std::vector<float> > ph_noniso_phi(reader, "ph_noniso_phi");
  TTreeReaderValue< std::vector<float> > ph_noniso_iso(reader, "ph_noniso_iso");
  TTreeReaderValue< std::vector<float> > ph_noniso_w(reader, "ph_noniso_w");

  TTreeReaderValue<int> jet_n(reader, "jet_n");
  TTreeReaderValue<int> bjet_n(reader, "bjet_n");
  TTreeReaderValue< std::vector<float> > jet_pt(reader, "jet_pt");
  TTreeReaderValue< std::vector<float> > jet_eta(reader, "jet_eta");
  TTreeReaderValue< std::vector<float> > jet_phi(reader, "jet_phi");
  TTreeReaderValue< std::vector<float> > jet_e(reader, "jet_e");
  TTreeReaderValue< std::vector<bool> >  jet_isb(reader, "jet_isb");
  TTreeReaderValue< std::vector<float> >  jet_w(reader, "jet_w");

  TTreeReaderValue<int> mu_n(reader, "mu_n");
  TTreeReaderValue< std::vector<float> > mu_pt(reader, "mu_pt");
  TTreeReaderValue< std::vector<float> > mu_eta(reader, "mu_eta");
  TTreeReaderValue< std::vector<float> > mu_phi(reader, "mu_phi");
  TTreeReaderValue< std::vector<int> > mu_ch(reader, "mu_ch");
  TTreeReaderValue< std::vector<float> > mu_w(reader, "mu_w");

  TTreeReaderValue<int> el_n(reader, "el_n");
  TTreeReaderValue< std::vector<float> > el_pt(reader, "el_pt");
  TTreeReaderValue< std::vector<float> > el_eta(reader, "el_eta");
  TTreeReaderValue< std::vector<float> > el_phi(reader, "el_phi");
  TTreeReaderValue< std::vector<int> >   el_ch(reader, "el_ch");
  TTreeReaderValue< std::vector<float> > el_w(reader, "el_w");

  TTreeReaderValue<float> met_phi(reader, "met_phi");
  TTreeReaderValue<float> met_et(reader, "met_et");
  TTreeReaderValue<float> ht(reader, "ht");
  TTreeReaderValue<float> meff(reader, "meff");
  TTreeReaderValue<float> rt2(reader, "rt2");
  TTreeReaderValue<float> rt4(reader, "rt4");

  TTreeReaderValue<float> dphi_jetmet(reader, "dphi_jetmet");
  TTreeReaderValue<float> dphi_gamjet(reader, "dphi_gamjet");
  TTreeReaderValue<float> dphi_gammet(reader, "dphi_gammet");

#ifdef EXTRA_VARS
  TTreeReaderValue<float> ht0(reader, "ht0");
  TTreeReaderValue<float> meff0(reader, "meff0");

  TTreeReaderValue<float> dphi_jetmet1(reader, "dphi_jetmet1");
  TTreeReaderValue<float> dphi_jetmet2(reader, "dphi_jetmet2");
  TTreeReaderValue<float> dphi_jetmet3(reader, "dphi_jetmet3");
  TTreeReaderValue<float> dphi_jetmet4(reader, "dphi_jetmet4");
  TTreeReaderValue<float> dphi_jetmetA(reader, "dphi_jetmetA");

  TTreeReaderValue<float> dphi_gamjet1(reader, "dphi_gamjet1");
  TTreeReaderValue<float> dphi_gamjet2(reader, "dphi_gamjet2");
  TTreeReaderValue<float> dphi_gamjet3(reader, "dphi_gamjet3");
  TTreeReaderValue<float> dphi_gamjet4(reader, "dphi_gamjet4");
  TTreeReaderValue<float> dphi_gamjetA(reader, "dphi_gamjetA");
#endif

  // New tree
  TFile *output_file = new TFile(output_path, "recreate");
  TTree *output_tree = new TTree("mini", "mini");

  int new_event;
  float new_avgmu;

  float new_weight_mc;
  float new_weight_pu;
  float new_weight_sf;
  float new_weight_fjg;

  int new_ph_n;
  int new_mu_n;
  int new_el_n;
  int new_jet_n;
  int new_bjet_n;

  float new_met_et;
  float new_met_phi;
  float new_ht;
  float new_meff;
  float new_rt2;
  float new_rt4;
  float new_dphi_jetmet;
  float new_dphi_gamjet;
  float new_dphi_gammet;

#ifdef EXTRA_VARS
  float new_ht0;
  float new_meff0;

  float new_dphi_gamjet1;
  float new_dphi_gamjet2;
  float new_dphi_gamjet3;
  float new_dphi_gamjet4;
  float new_dphi_gamjetA;

  float new_dphi_jetmet1;
  float new_dphi_jetmet2;
  float new_dphi_jetmet3;
  float new_dphi_jetmet4;
  float new_dphi_jetmetA;
#endif

  std::vector<float> *new_ph_pt = new std::vector<float>(); 
  std::vector<float> *new_ph_eta = new std::vector<float>();
  std::vector<float> *new_ph_phi = new std::vector<float>();
  std::vector<float> *new_ph_iso = new std::vector<float>();
  std::vector<float> *new_ph_w = new std::vector<float>();

  std::vector<float> *new_jet_pt = new std::vector<float>(); 
  std::vector<float> *new_jet_eta = new std::vector<float>();
  std::vector<float> *new_jet_phi = new std::vector<float>();
  std::vector<float> *new_jet_e = new std::vector<float>();
  std::vector<bool> *new_jet_isb = new std::vector<bool>();
  std::vector<float> *new_jet_w = new std::vector<float>();
  
  std::vector<float> *new_el_pt = new std::vector<float>(); 
  std::vector<float> *new_el_eta = new std::vector<float>();
  std::vector<float> *new_el_phi = new std::vector<float>();
  std::vector<int>   *new_el_ch = new std::vector<int>();
  std::vector<float> *new_el_w = new std::vector<float>();
  
  std::vector<float> *new_mu_pt = new std::vector<float>(); 
  std::vector<float> *new_mu_eta = new std::vector<float>();
  std::vector<float> *new_mu_phi = new std::vector<float>();
  std::vector<int>   *new_mu_ch = new std::vector<int>();
  std::vector<float> *new_mu_w = new std::vector<float>();

  output_tree->Branch("event", &new_event, "event/I");
  output_tree->Branch("avgmu", &new_avgmu, "avgmu/F");

  output_tree->Branch("weight_mc", &new_weight_mc);
  output_tree->Branch("weight_pu", &new_weight_pu);
  output_tree->Branch("weight_sf", &new_weight_sf);
  output_tree->Branch("weight_fjg", &new_weight_fjg);

  output_tree->Branch("ph_n", &new_ph_n, "ph_n/I");
  output_tree->Branch("ph_pt",  new_ph_pt);
  output_tree->Branch("ph_eta", new_ph_eta);
  output_tree->Branch("ph_phi", new_ph_phi);
  output_tree->Branch("ph_iso", new_ph_iso);
  output_tree->Branch("ph_w",   new_ph_w);

  output_tree->Branch("jet_n", &new_jet_n, "jet_n/I");
  output_tree->Branch("bjet_n", &new_bjet_n, "bjet_n/I");
  output_tree->Branch("jet_eta", new_jet_eta);
  output_tree->Branch("jet_phi", new_jet_phi);
  output_tree->Branch("jet_pt",  new_jet_pt);
  output_tree->Branch("jet_e",   new_jet_e);
  output_tree->Branch("jet_isb", new_jet_isb);
  output_tree->Branch("jet_w",  new_jet_w);
  
  output_tree->Branch("el_n", &new_el_n, "el_n/I");
  output_tree->Branch("el_eta", new_el_eta);
  output_tree->Branch("el_phi", new_el_phi);
  output_tree->Branch("el_pt",  new_el_pt);
  output_tree->Branch("el_ch",  new_el_ch);
  output_tree->Branch("el_w",   new_el_w);
  
  output_tree->Branch("mu_n", &new_mu_n, "mu_n/I");
  output_tree->Branch("mu_eta", new_mu_eta);
  output_tree->Branch("mu_phi", new_mu_phi);
  output_tree->Branch("mu_pt",  new_mu_pt);
  output_tree->Branch("mu_ch",  new_mu_ch);
  output_tree->Branch("mu_w",   new_mu_w);
  
  output_tree->Branch("met_et", &new_met_et);
  output_tree->Branch("met_phi", &new_met_phi);

  output_tree->Branch("ht", &new_ht);				
  output_tree->Branch("meff", &new_meff);				
  output_tree->Branch("rt2", &new_rt2);				
  output_tree->Branch("rt4", &new_rt4);				

  output_tree->Branch("dphi_gamjet", &new_dphi_gamjet);
  output_tree->Branch("dphi_jetmet", &new_dphi_jetmet);
  output_tree->Branch("dphi_gammet", &new_dphi_gammet);

#ifdef EXTRA_VARS
  output_tree->Branch("ht0", &new_ht0);				
  output_tree->Branch("meff0", &new_meff0);				

  output_tree->Branch("dphi_jetmet1", &new_dphi_jetmet1);
  output_tree->Branch("dphi_jetmet2", &new_dphi_jetmet2);
  output_tree->Branch("dphi_jetmet3", &new_dphi_jetmet3);  
  output_tree->Branch("dphi_jetmet4", &new_dphi_jetmet4);
  output_tree->Branch("dphi_jetmetA", &new_dphi_jetmetA);

  output_tree->Branch("dphi_gamjet1", &new_dphi_gamjet1);
  output_tree->Branch("dphi_gamjet2", &new_dphi_gamjet2);
  output_tree->Branch("dphi_gamjet3", &new_dphi_gamjet3);  
  output_tree->Branch("dphi_gamjet4", &new_dphi_gamjet4);
  output_tree->Branch("dphi_gamjetA", &new_dphi_gamjetA);
#endif

  
  // Loop over all entries of the TTree or TChain.
  long ientry = 0;
  int msg_interval = int(total_events/10);

  while(reader.Next()) {

    ientry++;

    if (total_events>10 && ientry%msg_interval == 0) 
      std::cout << "Processing event " << ientry << " of " << total_events << std::endl;

    // clear
    new_ph_pt->clear();
    new_ph_eta->clear();
    new_ph_phi->clear();
    new_ph_iso->clear();
    new_ph_w->clear();

    new_jet_pt->clear();
    new_jet_eta->clear();
    new_jet_phi->clear();
    new_jet_e->clear();
    new_jet_isb->clear();
    new_jet_w->clear();
    
    new_el_pt->clear();
    new_el_eta->clear();
    new_el_phi->clear();
    new_el_ch->clear();
    new_el_w->clear();
    
    new_mu_pt->clear();
    new_mu_eta->clear();
    new_mu_phi->clear();
    new_mu_ch->clear();
    new_mu_w->clear();

    new_ph_n = 0;
    new_mu_n = 0;
    new_el_n = 0;
    new_jet_n = 0;
    new_bjet_n = 0;
    
    new_met_et = 0;
    new_met_phi = 0;

    new_ht = 0;
    new_meff = 0;
    new_rt2	= 0;
    new_rt4	= 0;

    new_dphi_gamjet = 0;
    new_dphi_jetmet = 0;
    new_dphi_gammet = 0;

#ifdef EXTRA_VARS
    new_ht0		= 0;
    new_meff0	= 0;

    new_dphi_gamjet1 = 0;
    new_dphi_gamjet2 = 0;
    new_dphi_gamjet3 = 0;
    new_dphi_gamjet4 = 0;
    new_dphi_gamjetA = 0;
    
    new_dphi_jetmet1 = 0;
    new_dphi_jetmet2 = 0;
    new_dphi_jetmet3 = 0;
    new_dphi_jetmet4 = 0;
    new_dphi_jetmetA = 0;
#endif
    

    // fill
    if (*ph_n == 1 and (*ph_pt)[0] > 145)
      continue;
    
    new_el_n = *el_n;
    new_mu_n = *mu_n;
    new_jet_n = *jet_n;
    new_bjet_n = *bjet_n;

    new_ph_n = 0;
    for (int i=0; i<*ph_noniso_n; i++) {

      if ((*ph_noniso_pt)[i] < 145. || fabs((*ph_noniso_eta)[i]) > 2.37)
        continue;
      
      new_ph_n++;
      new_ph_pt->push_back((*ph_noniso_pt)[i]);
      new_ph_eta->push_back((*ph_noniso_eta)[i]);
      new_ph_phi->push_back((*ph_noniso_phi)[i]);
      new_ph_iso->push_back(0);
      new_ph_w->push_back(1.);
    }
    
    for (int i=0; i<*mu_n; i++) {
      new_mu_pt->push_back((*mu_pt)[i]);
      new_mu_eta->push_back((*mu_eta)[i]);
      new_mu_phi->push_back((*mu_phi)[i]);
      new_mu_ch->push_back((*mu_ch)[i]);
      new_mu_w->push_back((*mu_w)[i]);
    }


    for (int i=0; i<*el_n; i++) {
      new_el_pt->push_back((*el_pt)[i]);
      new_el_eta->push_back((*el_eta)[i]);
      new_el_phi->push_back((*el_phi)[i]);
      new_el_ch->push_back((*el_ch)[i]);
      new_el_w->push_back((*el_w)[i]);
    }

    for (int i=0; i<*jet_n; i++) {
        new_jet_pt->push_back((*jet_pt)[i]);
        new_jet_eta->push_back((*jet_eta)[i]);
        new_jet_phi->push_back((*jet_phi)[i]);
        new_jet_e->push_back((*jet_e)[i]);
        new_jet_w->push_back((*jet_w)[i]);
        new_jet_isb->push_back(0); //(*jet_isb)[i]);
    }

    // event
    new_event = *event;
    new_avgmu = *avgmu;
    
    new_weight_mc = *weight_mc;
    new_weight_pu = *weight_pu;
    new_weight_sf = *weight_sf;

    // others
    new_met_et  = *met_et;
    new_met_phi = *met_phi;

    new_rt2 = *rt2;
    new_rt4 = *rt4;
    new_dphi_jetmet = *dphi_jetmet;

#ifdef EXTRA_VARS
    new_ht0 = *ht0;
    new_meff0 = *meff0;

    new_dphi_jetmet1 = *dphi_jetmet1;
    new_dphi_jetmet2 = *dphi_jetmet2;
    new_dphi_jetmet3 = *dphi_jetmet3;
    new_dphi_jetmet4 = *dphi_jetmet4;
    new_dphi_jetmetA = *dphi_jetmetA;
#endif

    Float_t dphi1 = 4.;
    Float_t dphi2 = 4.;
    Float_t dphi3 = 4.;
    Float_t dphi4 = 4.;
    if (*ph_noniso_n > 0) {
      new_dphi_gammet = get_dphi((*ph_noniso_phi)[0], *met_phi);

      if (*jet_n > 0) new_dphi_gamjet = get_dphi((*ph_noniso_phi)[0], (*jet_phi)[0]);

      if (*jet_n > 0) dphi1 = get_dphi((*ph_noniso_phi)[0], (*jet_phi)[0]);
      if (*jet_n > 1) dphi2 = get_dphi((*ph_noniso_phi)[0], (*jet_phi)[1]);
      if (*jet_n > 2) dphi3 = get_dphi((*ph_noniso_phi)[0], (*jet_phi)[2]);
      if (*jet_n > 3) dphi4 = get_dphi((*ph_noniso_phi)[0], (*jet_phi)[3]);
    }

    new_dphi_gamjet = dphi1;

#ifdef EXTRA_VARS
    new_dphi_gamjet1 = dphi1;
    new_dphi_gamjet2 = TMath::Min(new_dphi_gamjet1, dphi2);
    new_dphi_gamjet3 = TMath::Min(new_dphi_gamjet2, dphi3);
    new_dphi_gamjet4 = TMath::Min(new_dphi_gamjet3, dphi4);
#endif

    new_ht = *ht;
    if (*ph_n > 0)
      new_ht -= (*ph_pt)[0];
    if (new_ph_n > 0)
      new_ht += (*ph_noniso_pt)[0];

    new_meff = new_ht + new_met_et;

    if (new_ph_n > 0) {
      unsigned int pt_bin  = get_pt_bin((*ph_noniso_pt)[0]);
      unsigned int eta_bin = get_eta_bin((*ph_noniso_eta)[0]);

      new_weight_fjg = fjg_factor[eta_bin*3+pt_bin];

      output_tree->Fill();
    }

  }

  // just for consistency. They are wrong
  TH1D *events = (TH1D*)f->Get("events");
  TH1D *cutflow = (TH1D*)f->Get("cutflow");
    
  if (events) events->Write(); 
  if (cutflow) cutflow->Write(); 

  output_tree->Write();
  output_file->Close();
}

int main(int argc, char *argv[]) 
{
  if (argc < 3) {
    std::cout << "usage: create_jfake_mini <input_file> <output_file>" << std::endl;
    return 1;
  }

  TString input_file = argv[1];
  TString output_file = argv[2];

  loop(input_file, output_file);

  return 0;
}
