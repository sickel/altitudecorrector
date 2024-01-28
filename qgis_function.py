from qgis.core import *
from qgis.gui import *
import math

@qgsfunction(args='auto', group='Gamma')
def altitudecorrection(value, altitude, water0m, waterslope, landattenuation, feature, parent):
    """
    Does altitude correction on gross measurements estimates the value at 1m above ground.
    <h2>Example usage:</h2>
    <ul>
    <li>altitudecorr("value","altitude",water0m, waterslope,landattenuation) -> Estimated value at 1 meter</li>
    </ul>
    </h3>Typical values for dose rate:</h3><br />
    water0m = 4.284670<br />
    waterslope = 0.001743<br />
    landattenuation = 0.006383
    :param value: The field that is to be corrected
    :param altitude: The field that holds altitude above surface correction.
    :param water0m: The estimated value at water surface
    :param waterslope: The estimated slope over water
    :param landattenuation: The estimated attenuation factor over land
    :return: etimated value for 1 meter above ground

    """
    
    ntb = water0m + waterslope * altitude
    ntb1 = water0m + waterslope 
    if landattenuation > 0:
        landattenuation = -1 * landattenuation
    gmmdown= (value-ntb) * math.exp(landattenuation)/math.exp(landattenuation*altitude) + ntb1
    return gmmdown
