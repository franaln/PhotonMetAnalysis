// only keep jets with pt>30 and |eta|<2.5

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

Float_t get_dphi(Float_t phi1, Float_t phi2)
{
  Float_t  phi = fabs(phi1 - phi2);
  if(phi <= TMath::Pi())  return phi;
  else                    return (2 * TMath::Pi() - phi);
}

struct Jet
{
  Float_t pt;
  Float_t eta;
  Float_t phi;
  Float_t e;
  Float_t w;
  Int_t isb;
};

 
bool ptsorter(Jet j1, Jet j2) {
  return ( j1.pt > j2.pt );
}

void loop(TString input_path, TString output_path)
{

  bool m_ismc = true;
  if (input_path.Contains("data"))
    m_ismc = false;

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

  std::cout << "fix_jets: " << input_path << " -> " << output_path << std::endl;

  TTreeReaderValue< int> event_number(reader, "event_number");
  TTreeReaderValue< int> avg_mu(reader, "avg_mu");

  TTreeReaderValue<float> weight_mc(reader, "weight_mc");
  TTreeReaderValue<float> weight_pu(reader, "weight_pu");
  TTreeReaderValue<float> weight_sf(reader, "weight_sf");

  TTreeReaderValue< int> ph_n(reader, "ph_n");
  TTreeReaderValue< std::vector<float> > ph_pt(reader, "ph_pt");
  TTreeReaderValue< std::vector<float> > ph_eta(reader, "ph_eta");
  TTreeReaderValue< std::vector<float> > ph_phi(reader, "ph_phi");
  TTreeReaderValue< std::vector<float> > ph_iso(reader, "ph_iso");
  TTreeReaderValue< std::vector<float> > ph_w(reader, "ph_w");

  TTreeReaderValue< int> ph_noniso_n(reader, "ph_noniso_n");
  TTreeReaderValue< std::vector<float> > ph_noniso_pt(reader, "ph_noniso_pt");
  TTreeReaderValue< std::vector<float> > ph_noniso_eta(reader, "ph_noniso_eta");
  TTreeReaderValue< std::vector<float> > ph_noniso_phi(reader, "ph_noniso_phi");
  TTreeReaderValue< std::vector<float> > ph_noniso_iso(reader, "ph_noniso_iso");
  TTreeReaderValue< std::vector<float> > ph_noniso_w(reader, "ph_noniso_w");

  TTreeReaderValue< int> ph_loose_n(reader, "ph_loose_n");
  TTreeReaderValue< std::vector<float> > ph_loose_pt(reader, "ph_loose_pt");
  TTreeReaderValue< std::vector<float> > ph_loose_eta(reader, "ph_loose_eta");
  TTreeReaderValue< std::vector<float> > ph_loose_phi(reader, "ph_loose_phi");
  TTreeReaderValue< std::vector<float> > ph_loose_iso20(reader, "ph_loose_iso20");
  TTreeReaderValue< std::vector<float> > ph_loose_iso40(reader, "ph_loose_iso40");

  TTreeReaderValue< int> jet_n(reader, "jet_n");
  TTreeReaderValue< std::vector<float> > jet_pt(reader, "jet_pt");
  TTreeReaderValue< std::vector<float> > jet_eta(reader, "jet_eta");
  TTreeReaderValue< std::vector<float> > jet_phi(reader, "jet_phi");
  TTreeReaderValue< std::vector<float> > jet_e(reader, "jet_e");
  TTreeReaderValue< std::vector<bool> >  jet_isb(reader, "jet_isb");
  TTreeReaderValue< std::vector<float> >  jet_w(reader, "jet_w");

  TTreeReaderValue< int> mu_n(reader, "mu_n");
  TTreeReaderValue< std::vector<float> > mu_pt(reader, "mu_pt");
  TTreeReaderValue< std::vector<float> > mu_eta(reader, "mu_eta");
  TTreeReaderValue< std::vector<float> > mu_phi(reader, "mu_phi");
  TTreeReaderValue< std::vector<int> > mu_ch(reader, "mu_ch");
  TTreeReaderValue< std::vector<float> > mu_w(reader, "mu_w");

  TTreeReaderValue< int> el_n(reader, "el_n");
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


  // New tree
  TFile *output_file = new TFile(output_path, "recreate");
  TTree *output_tree = new TTree("mini", "mini");

  int new_event_number;
  int new_avg_mu;

  float new_weight_mc;
  float new_weight_pu;
  float new_weight_sf;

  int new_ph_loose_n;
  int new_ph_n;
  int new_ph_noniso_n;
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

  float new_ht0;
  float new_meff0;

  float new_dphi_jetmet;
  float new_dphi_gamjet;
  float new_dphi_gammet;

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


  std::vector<float> *new_ph_loose_pt = new std::vector<float>(); 
  std::vector<float> *new_ph_loose_eta = new std::vector<float>();
  std::vector<float> *new_ph_loose_phi = new std::vector<float>();
  std::vector<unsigned int> *new_ph_loose_isem = new std::vector<unsigned int>();
  std::vector<float> *new_ph_loose_iso20 = new std::vector<float>();
  std::vector<float> *new_ph_loose_iso40 = new std::vector<float>();

  std::vector<float> *new_ph_pt = new std::vector<float>(); 
  std::vector<float> *new_ph_eta = new std::vector<float>();
  std::vector<float> *new_ph_phi = new std::vector<float>();
  std::vector<float> *new_ph_iso = new std::vector<float>();
  std::vector<float> *new_ph_w = new std::vector<float>();

  std::vector<float> *new_ph_truth_pt = new std::vector<float>(); 
  std::vector<float> *new_ph_truth_eta = new std::vector<float>();
  std::vector<float> *new_ph_truth_phi = new std::vector<float>();
  std::vector<int> *new_ph_truth_id = new std::vector<int>();
  std::vector<int> *new_ph_truth_type = new std::vector<int>();
  std::vector<int> *new_ph_truth_origin = new std::vector<int>();
  

  std::vector<float> *new_ph_noniso_pt = new std::vector<float>(); 
  std::vector<float> *new_ph_noniso_eta = new std::vector<float>();
  std::vector<float> *new_ph_noniso_phi = new std::vector<float>();
  std::vector<float> *new_ph_noniso_iso = new std::vector<float>();
  std::vector<float> *new_ph_noniso_w = new std::vector<float>();

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

  output_tree->Branch("event_number", &new_event_number, "event_number/I");
  output_tree->Branch("avg_mu", &new_avg_mu, "avg_mu/I");

  output_tree->Branch("weight_mc", &new_weight_mc);
  output_tree->Branch("weight_pu", &new_weight_pu);
  output_tree->Branch("weight_sf", &new_weight_sf);
  
  output_tree->Branch("ph_loose_n", &new_ph_loose_n, "ph_loose_n/I");
  output_tree->Branch("ph_loose_eta", new_ph_loose_eta);
  output_tree->Branch("ph_loose_phi", new_ph_loose_phi);
  output_tree->Branch("ph_loose_pt",  new_ph_loose_pt);
  output_tree->Branch("ph_loose_iso20",  new_ph_loose_iso20);
  output_tree->Branch("ph_loose_iso40",  new_ph_loose_iso40);

  output_tree->Branch("ph_n", &new_ph_n, "ph_n/I");
  output_tree->Branch("ph_pt",  new_ph_pt);
  output_tree->Branch("ph_eta", new_ph_eta);
  output_tree->Branch("ph_phi", new_ph_phi);
  output_tree->Branch("ph_iso", new_ph_iso);
  output_tree->Branch("ph_w",   new_ph_w);

  if (m_ismc) {
    output_tree->Branch("ph_truth_pt",  new_ph_truth_pt);
    output_tree->Branch("ph_truth_eta", new_ph_truth_eta);
    output_tree->Branch("ph_truth_phi", new_ph_truth_phi);
    output_tree->Branch("ph_truth_id",  new_ph_truth_id);
    output_tree->Branch("ph_truth_type", new_ph_truth_type);
    output_tree->Branch("ph_truth_origin", new_ph_truth_origin);
  }

  output_tree->Branch("ph_noniso_n", &new_ph_noniso_n, "ph_noniso_n/I");
  output_tree->Branch("ph_noniso_pt",  new_ph_noniso_pt);
  output_tree->Branch("ph_noniso_eta", new_ph_noniso_eta);
  output_tree->Branch("ph_noniso_phi", new_ph_noniso_phi);
  output_tree->Branch("ph_noniso_iso", new_ph_noniso_iso);
  output_tree->Branch("ph_noniso_w",   new_ph_noniso_w);

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

  output_tree->Branch("ht0", &new_ht0);				
  output_tree->Branch("meff0", &new_meff0);				

  output_tree->Branch("dphi_gamjet", &new_dphi_gamjet);
  output_tree->Branch("dphi_jetmet", &new_dphi_jetmet);
  output_tree->Branch("dphi_gammet", &new_dphi_gammet);

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

  
  // Loop over all entries of the TTree or TChain.
  long ientry = 0;
  int msg_interval = int(total_events/10);
  while(reader.Next()) {

    ientry++;

    if (total_events>10 && ientry%msg_interval == 0) 
      std::cout << "Processing event " << ientry << " of " << total_events << std::endl;

    // clear
    new_ph_loose_pt->clear();
    new_ph_loose_eta->clear(); 
    new_ph_loose_phi->clear(); 
    new_ph_loose_isem->clear();
    new_ph_loose_iso20->clear();
    new_ph_loose_iso40->clear();

    new_ph_pt->clear();
    new_ph_eta->clear();
    new_ph_phi->clear();
    new_ph_iso->clear();
    new_ph_w->clear();

    if (m_ismc) {
      new_ph_truth_pt->clear();
      new_ph_truth_eta->clear();
      new_ph_truth_phi->clear();
      new_ph_truth_id->clear();
      new_ph_truth_type->clear();
      new_ph_truth_origin->clear();
    }

    new_ph_noniso_pt->clear();
    new_ph_noniso_eta->clear();
    new_ph_noniso_phi->clear();
    new_ph_noniso_iso->clear();
    new_ph_noniso_w->clear();
    
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

    new_ph_loose_n = 0;
    new_ph_n = 0;
    new_ph_noniso_n = 0;
    new_mu_n = 0;
    new_el_n = 0;
    new_jet_n = 0;
    new_bjet_n = 0;
    
    new_met_et = 0;
    new_met_phi = 0;

    new_ht		= 0;
    new_meff	= 0;
    new_rt2		= 0;
    new_rt4		= 0;

    new_ht0		= 0;
    new_meff0	= 0;

    new_dphi_gamjet = 0;
    new_dphi_jetmet = 0;
    new_dphi_gammet = 0;

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
    

    // fill
    new_ph_n = *ph_n;
    new_ph_noniso_n = *ph_noniso_n;
    new_ph_loose_n = *ph_loose_n;
    new_el_n = *el_n;
    new_mu_n = *mu_n;
    new_jet_n = 0;
    new_bjet_n = 0;

    for (int i=0; i<*ph_n; i++) {
      new_ph_pt->push_back((*ph_pt)[i]);
      new_ph_eta->push_back((*ph_eta)[i]);
      new_ph_phi->push_back((*ph_phi)[i]);
      new_ph_iso->push_back((*ph_iso)[i]);
      new_ph_w->push_back((*ph_w)[i]);
    }
    
    for (int i=0; i<*ph_noniso_n; i++) {
      new_ph_noniso_pt->push_back((*ph_noniso_pt)[i]);
      new_ph_noniso_eta->push_back((*ph_noniso_eta)[i]);
      new_ph_noniso_phi->push_back((*ph_noniso_phi)[i]);
      new_ph_noniso_iso->push_back((*ph_noniso_iso)[i]);
      new_ph_noniso_w->push_back((*ph_noniso_w)[i]);
    }

    for (int i=0; i<*ph_loose_n; i++) {
      new_ph_loose_pt->push_back((*ph_loose_pt)[i]);
      new_ph_loose_eta->push_back((*ph_loose_eta)[i]);
      new_ph_loose_phi->push_back((*ph_loose_phi)[i]);
      new_ph_loose_iso20->push_back((*ph_loose_iso20)[i]);
      new_ph_loose_iso40->push_back((*ph_loose_iso40)[i]);
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

    // for (int i=0; i<*jet_n; i++) {

    //   if (fabs((*jet_eta)[i]) < 2.5 && (*jet_pt)[i] > 30) {
                
    //     new_jet_pt->push_back((*jet_pt)[i]);
    //     new_jet_eta->push_back((*jet_eta)[i]);
    //     new_jet_phi->push_back((*jet_phi)[i]);
    //     new_jet_e->push_back((*jet_e)[i]);
    //     new_jet_w->push_back((*jet_w)[i]);

    //     new_jet_n++;
    //     if ((*jet_isb)[i] == 1) {
    //       new_bjet_n++;
    //       new_jet_isb->push_back(1);
    //     }
    //   }
    // }

    std::vector<Jet> jets;
    for (int i=0; i<*jet_n; i++) {

      if (fabs((*jet_eta)[i]) < 2.5 && (*jet_pt)[i] > 30) {
                
        Jet j;
        j.pt  = (*jet_pt)[i];
        j.eta = (*jet_eta)[i];
        j.phi = (*jet_phi)[i];
        j.e   = (*jet_e)[i];
        j.w   = (*jet_w)[i];
        j.isb = 0;

        new_jet_n++;
        if ((*jet_isb)[i] == 1) {
          new_bjet_n++;
          j.isb  = 1;
        }

        jets.push_back(j);
      }
    }

    std::sort (jets.begin(), jets.end(), ptsorter); 

    for (auto j : jets) {
      new_jet_pt->push_back(j.pt);
      new_jet_eta->push_back(j.eta);
      new_jet_phi->push_back(j.phi);
      new_jet_e->push_back(j.e);
      new_jet_w->push_back(j.w);
      new_jet_isb->push_back(j.isb);
    }

    // event
    new_event_number = *event_number;
    new_avg_mu = *avg_mu;
    
    new_weight_mc = *weight_mc;
    new_weight_pu = *weight_pu;
    new_weight_sf = *weight_sf;

    // others
    new_met_et  = *met_et;
    new_met_phi = *met_phi;

    Double_t sum_jet_pt = 0.0;
    Double_t sum_jet2_pt = 0.0;
    Double_t sum_jet4_pt = 0.0;
    
    for (int i=0; i<new_jet_n; i++) {

      Double_t pt = jets[i].pt;
      if (new_jet_n >= 2 && i < 2)
        sum_jet2_pt += pt;
      if (new_jet_n >= 4 && i < 4)
        sum_jet4_pt += pt;
      sum_jet_pt += pt;
    }

    // Ht
    new_ht0 = sum_jet_pt;
    new_ht = sum_jet_pt;
    if (new_ph_n > 0)
      new_ht += (*new_ph_pt)[0];

    // Meff
    new_meff0 = new_ht0 + new_met_et;
    new_meff = new_ht + new_met_et;

    // Rt
    new_rt2 = sum_jet2_pt/sum_jet_pt;
    new_rt4 = sum_jet4_pt/sum_jet_pt;
  
    // dphi between met and jet
    Float_t dphi1 = 4.;
    Float_t dphi2 = 4.;
    Float_t dphi3 = 4.;
    Float_t dphi4 = 4.;
    if (new_jet_n > 0) dphi1 = get_dphi(jets[0].phi, new_met_phi);
    if (new_jet_n > 1) dphi2 = get_dphi(jets[1].phi, new_met_phi);
    if (new_jet_n > 2) dphi3 = get_dphi(jets[2].phi, new_met_phi);
    if (new_jet_n > 3) dphi4 = get_dphi(jets[3].phi, new_met_phi);
  
    new_dphi_jetmet = TMath::Min(dphi1, dphi2);

    new_dphi_jetmet1 = dphi1;
    new_dphi_jetmet2 = TMath::Min(new_dphi_jetmet1, dphi2);
    new_dphi_jetmet3 = TMath::Min(new_dphi_jetmet2, dphi3);
    new_dphi_jetmet4 = TMath::Min(new_dphi_jetmet3, dphi4);

    Float_t dphi_jetmetA_tmp = 4.;
    for (int i=0; i<new_jet_n; i++) {
      dphi_jetmetA_tmp = TMath::Min(get_dphi(jets[i].phi, new_met_phi), dphi_jetmetA_tmp);
    }
    new_dphi_jetmetA = dphi_jetmetA_tmp;

    // dphi between leading photon and jet
    dphi1 = 4.;
    dphi2 = 4.;
    dphi3 = 4.;
    dphi4 = 4.;
    if (new_ph_n > 0) {
      if (new_jet_n > 0) dphi1 = get_dphi((*new_ph_phi)[0], jets[0].phi);
      if (new_jet_n > 1) dphi2 = get_dphi((*new_ph_phi)[0], jets[1].phi);
      if (new_jet_n > 2) dphi3 = get_dphi((*new_ph_phi)[0], jets[2].phi);
      if (new_jet_n > 3) dphi4 = get_dphi((*new_ph_phi)[0], jets[3].phi);
    }

    new_dphi_gamjet = dphi1;

    new_dphi_gamjet1 = dphi1;
    new_dphi_gamjet2 = TMath::Min(new_dphi_gamjet1, dphi2);
    new_dphi_gamjet3 = TMath::Min(new_dphi_gamjet2, dphi3);
    new_dphi_gamjet4 = TMath::Min(new_dphi_gamjet3, dphi4);

    Float_t dphi_gamjetA_tmp = 4.;
    if (new_ph_n > 0) {
      for (int i=0; i<new_jet_n; i++) {
        dphi_gamjetA_tmp = TMath::Min(get_dphi((*new_ph_phi)[0], jets[i].phi), dphi_gamjetA_tmp);
      }
    }
    new_dphi_gamjetA    = dphi_gamjetA_tmp;


    // dphi beteen photon and met
    new_dphi_gammet = *dphi_gammet;

    //if (new_ph_n == 1) 
    output_tree->Fill();
  }


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
    std::cout << "usage: fix_jets <input_file> <output_file>" << std::endl;
    return 1;
  }

  TString input_file = argv[1];
  TString output_file = argv[2];

  loop(input_file, output_file);

  return 0;
}
