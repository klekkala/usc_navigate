import Equirec2Perspec as E2P

new_min = -100
new_max = 100
lat_min = 40.42524817            ## this is for first 500 in pittsburg need to generalize this for all places
lat_max = 40.44497464
long_min = -80.03468568
long_max = -79.98858816

theta = 45
image = "3xBZaaUK877tjKQ7ELbFsQ"

equ = E2P.Equirectangular("data/Pittsburgh/"+image+".jpg")  # Load equirectangular image
img = equ.GetPerspective(90, -theta, 0, 720, 1080)  # Specify parameters(FOV, theta, phi, height, width)

print(img.shape)