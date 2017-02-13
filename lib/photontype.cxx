int photontype(int truth_type, int truth_origin)
{
  int type = 3;
  if (truth_type == 2) { // iso electron
    if (truth_origin == 12) // coming from W
      type = 1;
    else if (truth_origin == 13) // coming from Z
      type = 1;
  }

  else if (truth_type == 4) { // bkg electron
    if (truth_origin == 5) // photon conversion
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
    if (truth_origin == 23) // light meson
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
