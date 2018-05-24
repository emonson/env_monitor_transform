# https://en.wikipedia.org/wiki/Dew_point
import numpy as np

def tdf_np(Tf:np.array, RH:np.array) -> np.array:
  # NOAA constants
  a = 6.1121
  b = 17.67
  c = 243.5
  
  Tc = (Tf-32)/1.8
  gamma = np.log(RH/100.0) + (b*Tc)/(c + Tc)
  Pa = a*np.exp(gamma)
  x = np.log(Pa/a)
  Tdp = c*x / (b - x)
  
  Tdf = Tdp * 1.8 + 32.0
  
  return Tdf