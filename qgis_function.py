from qgis.core import *
from qgis.gui import *
import math

@qgsfunction(args='auto', group='Gamma')
def altitudecorrection_2(value, altitude, water0m, waterslope, landslope, feature, parent):
    """
    Does altitude correction on gross measurements.
    <h2>Example usage:</h2>
    <ul>
    <li>altitudecorr("valuefield","altitudefield",ywater,waterslope,landslope) -> Value at 1 meter</li>
    </ul>
    </h3>Typical values for dose rate:</h3><br />
    ywater = 4.284670<br />
    waterslope = 0.001743<br />
    landslope = -0.006383
    
 
    """
    
    """
    The formula that we made in Geosoft to correct dose rate to 1m above ground is;

    GMM_DOSE_DOWN_CORR = (GMM_DOSE_DOWN - @theNTB)*exp(-0.006383)/exp(-0.006383*@theAltitude)+ @theNTB0;
    ntb = ywater + waterslope * altitude
    corr = (value - ntb) * exp(-landslope)/exp(-landslope*altitude) + ntb
    Where:
    @theNTB = 4.284670 + 0.001743*@theAltitude;
               Where: 4.284670 is Y intercept (non-terrestrial background) of Altitude vs Dose for flights over water
                0.001743 is slope of Altitude vs Dose for flights over water
    @theNTB0 = 4.284670 + 0.001743*1.0 ;
    -0.006383 is slope (attenuation coefficient) of line in Altitude vs Dose for flights over land
    
    """
    # For gross count:
    #ntb=997.176 + 0.423522*altitude
    #ntb0=997.176 + 0.423522
    #ntb=4.284670
    #ntbfactor=0.001743
    ntb = water0m + waterslope * altitude
    ntb1 = water0m + waterslope 
    if landslope > 0:
        landslope = -1 * landslope
    gmmdown= (value-ntb) * math.exp(landslope)/math.exp(landslope*altitude) + ntb1
    return gmmdown
