float get_dphi(float phi1, float phi2)
{
  float  phi = fabs(phi1 - phi2);
  if (phi <= TMath::Pi())  return phi;
  else                     return (2 * TMath::Pi() - phi); 
}

// type: 0=photon, 1=electron, 2=jet, 3=other
int photontype(int truth_type, int truth_origin)
{
  int type = 3;
  if (truth_type == 2) { // iso electron
    if (truth_origin == 10) // coming from top
      type = 1;
    else if (truth_origin == 12) // coming from W
      type = 1;
    else if (truth_origin == 13) // coming from Z
      type = 1;
  }

  else if (truth_type == 4) { // bkg electron
    if (truth_origin == 5) // photon conversion
      type = 0;
  }
   
  else if (truth_type == 13) { // unknown y (mainly for tty, probably isr/fsr photons)
    type = 0;
  }

  else if (truth_type == 14) { // isolated y
    if (truth_origin == 3) // single y
      type = 0;
    else if  (truth_origin == 37) // prompt y
      type = 0;
  }

  else if (truth_type == 15) { // non-isolated y
    if (truth_origin == 9) // tau
      type = 2;
    else if (truth_origin == 39 || truth_origin == 40) // ISR or FSR
      type = 0;
  }

  else if (truth_type == 16) { // background y
    if (truth_origin >= 23 && truth_origin <= 35) // meson, baryon decays
      type = 2;
    else if (truth_origin == 38) // underline (?)
      type = 2;
    else if (truth_origin == 42) // pi0
      type = 2;
  }

  else if (truth_type == 17) { // Hadron
    type = 2;
  }

  return type;
}


float m_inv(float pt1, float eta1, float phi1, float e1, float pt2, float eta2, float phi2, float e2)
{

  TLorentzVector tlv1;
  TLorentzVector tlv2;

  tlv1.SetPtEtaPhiE(pt1, eta1, phi1, e1);
  tlv2.SetPtEtaPhiE(pt2, eta2, phi2, e2);

  TLorentzVector tlv = tlv1 + tlv2;

  return tlv.M();
}


