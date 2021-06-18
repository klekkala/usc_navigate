import Equirec2Perspec as E2P
import data_helper as dh

o = dh.dataHelper()
image = "3xBZaaUK877tjKQ7ELbFsQ"

thetas = [0, 90 ,180, 270, 360 ]

for theta in thetas:

    o.panorama_split(theta, image)
