from qgis.core import *
from qgis.gui import *
import math

@qgsfunction(args='auto', group='Gamma')
def altitudecorrection(value1, value2, ntb,ntbfactor,expfactor, feature, parent):
    """
    Does altitude correction on gross measurements.
    <h2>Example usage:</h2>
    <ul>
    <li>altitudecorr("valuefield","altitudefield",ntb,ntbfactor,expfactor) -> Value at 1 meter</li>
    </ul>
    </h3>Possible values:</h3><br />
    ntb=4.284670<br />
    ntbfactor=0.001743<br />
    expfactor=-0.006383
    
    """
    
    
    # For gross count:
    #ntb=997.176 + 0.423522*value2
    #ntb0=997.176 + 0.423522
    #ntb=4.284670
    #ntbfactor=0.001743
    ntb0=ntb+ntbfactor
    #expfactor=-0.006383
    gmmdown=(value1-ntb)*math.exp(expfactor)/math.exp(expfactor*value2)+ ntb0
    return gmmdown
