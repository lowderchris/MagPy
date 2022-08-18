# Blender script to plot a coronal field distribution

# exec(open("/Users/clowder/research/solview/plt-sun.py").read())

# Import Python libraries
import matplotlib.image
import numpy
import sys
sys.path.append('/usr/local/lib/python3.7/site-packages')
import numpy as np
import sunpy.io
from PIL import Image

# Import blender rendering libraries
import bpy
from mathutils import Vector

# Define directory paths and data
datdir = '/Users/clowder/data/'
sys.path.append('/Users/clowder/research/solview/')
#sys.path.append('.')
fname = 'adapt-gong/adapt40311_02a012_201708030000_i00030600n0.fts'
cr = '0000'
ver = ''
step = '100000'

# Define some functions
def MakePolyLine(objname, curvename, cList, flmat):
    curvedata = bpy.data.curves.new(name=curvename, type='CURVE')
    curvedata.dimensions = '3D'
    #
    objectdata = bpy.data.objects.new(objname, curvedata)
    objectdata.location = (0,0,0) #object origin
    bpy.context.collection.objects.link(objectdata)
    #
    polyline = curvedata.splines.new('POLY')
    polyline.points.add(len(cList)-1)
    for num in range(len(cList)):
        polyline.points[num].co = (cList[num])+(w,)
    #
    polyline.order_u = 0
    polyline.use_endpoint_u = True
    #
    objectdata.data.fill_mode = 'FULL'
    # objectdata.data.bevel_depth = 0.005 - CL CHANGE THIS BACK
    objectdata.data.bevel_depth = 0.0525
    objectdata.data.bevel_resolution = 5
    #
    objectdata.active_material = flmat

def MakeSmoothPolyLine(objname, curvename, cList, flmat):
    curvedata = bpy.data.curves.new(name=curvename, type='CURVE')
    curvedata.dimensions = '3D'
    #
    objectdata = bpy.data.objects.new(objname, curvedata)
    objectdata.location = (0,0,0) #object origin
    bpy.context.collection.objects.link(objectdata)
    #
    polyline = curvedata.splines.new('NURBS')
    polyline.points.add(len(cList)-1)
    for num in range(len(cList)):
        polyline.points[num].co = (cList[num])+(w,)
    #
    polyline.order_u = len(polyline.points)-1
    #polyline.order_u = 0 # For direct fluxon plotting
    polyline.use_endpoint_u = True
    #
    objectdata.data.fill_mode = 'FULL'
    objectdata.data.bevel_depth = 0.005
    objectdata.data.bevel_resolution = 5
    #
    objectdata.active_material = flmat

# Read the world
from rdworld import rdworld
world = rdworld(datdir+'fluxon/cr'+cr+ver+'/cr'+cr+'-rlx'+step+'.flux')
#world = rdworld(datdir+'fluxon/cr'+cr+'/rlx/cr'+cr+'-rlx'+step+'.flux')

# Read surface magnetogram
def real_magnetogram(datdir, fname):
    br = (sunpy.io.fits.read(datdir + fname))[0].data[2,:,:]
    br = br - np.mean(br)
    #br = np.flip(br, axis=0)
    return br

br = real_magnetogram(datdir, fname)

matplotlib.image.imsave('br.png', np.clip(br,-20,20), cmap='Greys_r')

# Remove the default companion cube and lamp
objs = bpy.data.objects
objs.remove(objs["Cube"])
objs.remove(objs["Light"])

# Create a photosphere
sol = bpy.ops.mesh.primitive_uv_sphere_add(segments=360, ring_count=180, radius=1, location=[0,0,0], rotation=[0,0,np.pi])
bpy.ops.object.shade_smooth()
sol = bpy.data.objects['Sphere']

brmat = bpy.data.materials.new("BRMAT")
brmat.use_nodes = True
bsdf = brmat.node_tree.nodes["Principled BSDF"]
texImage = brmat.node_tree.nodes.new('ShaderNodeTexImage')
texImage.image = bpy.data.images.load('/Users/clowder/research/solview/br.png')
brmat.node_tree.links.new(bsdf.inputs['Base Color'], texImage.outputs['Color'])
brmat.node_tree.nodes["Principled BSDF"].inputs[5].default_value = 0
sol.data.materials.append(brmat)

# weight
w = 1

# Create some color materials
bmat = bpy.data.materials.new("BMAT")
bmat.diffuse_color = (83/255,103/255,113/255,1)
bmat.specular_intensity = 0
rmat = bpy.data.materials.new("RMAT")
rmat.diffuse_color = (125/255,77/255,77/255,1)
rmat.specular_intensity = 0
nmat = bpy.data.materials.new("NMAT")
nmat.diffuse_color = (101/255,89/255,107/255,1)
nmat.specular_intensity = 0

# Loop through world fieldlines and generate line objects
# Plot all closed fieldlines, and a sampling of open fieldlines
ofcount = 0
ofsample = 1

for i in numpy.arange(0, len(world.fx.id), 1):
    fl = []
    for j in numpy.arange(0, len(world.fx.x[i])):
        fl.append((world.fx.x[i][j], world.fx.y[i][j], world.fx.z[i][j]))
    if ((world.fx.fc0[i] == -1) or (world.fx.fc1[i] == -1)):
        flmat = bmat
        oftoggle = 1
        ofcount += 1
    elif ((world.fx.fc0[i] == -2) or (world.fx.fc1[i] == -2)):
        flmat = rmat
        oftoggle = 1
        ofcount += 1
    else:
        flmat = nmat
        oftoggle = 0
    if ((oftoggle == 0) or ((oftoggle == 1) and (np.mod(ofcount,ofsample)==0))):
        MakePolyLine("flo"+str(world.fx.id[i]), "flc"+str(world.fx.id[i]), fl, flmat)

# Lights!
bpy.context.scene.world.node_tree.nodes["Background"].inputs[0].default_value = (1,1,1,1)
bpy.context.scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value = 1

# Where we're going, we won't need ears...
# Sort out how to disable audio to allow computer sleep
# bpy.types.PreferencesSystem.audio_device = 'Null'

#bpy.data.lights.new(name="lamp1", type='AREA')
#bpy.data.objects["Hemi"].rotation_euler[1] = 180*(numpy.pi/180.0)
#bpy.ops.object.lamp_add(type='HEMI')
#bpy.types.World["World"].color=(1,1,1)

# Lights!
#bpy.ops.object.light_add(type='SUN', radius=1, location=(0,0,100), rotation=(0,0,0))
#bpy.ops.object.light_add(type='SUN', radius=1, location=(0,0,-100), rotation=(np.pi,0,0))

#bpy.ops.object.light_add(type='SUN', radius=1, location=(0,-30,0), rotation=(90*np.pi/180.,0,0))

# Camera!
#bpy.data.scenes['Scene'].camera.location.x = 0
#bpy.data.scenes['Scene'].camera.location.y = -10
#bpy.data.scenes['Scene'].camera.location.z = 0
#
#bpy.data.scenes['Scene'].camera.rotation_mode = 'XYZ'
#bpy.data.scenes['Scene'].camera.rotation_euler[0] = 90*(numpy.pi/180.0)
#bpy.data.scenes['Scene'].camera.rotation_euler[1] = 0*(numpy.pi/180.0)
#bpy.data.scenes['Scene'].camera.rotation_euler[2] = 0*(numpy.pi/180.0)
#
#bpy.data.cameras[bpy.context.scene.camera.name].clip_end = 500
#
## Render!
##bpy.data.scenes['Scene'].eevee.use_gtao = 1     # Some light shadowing
#bpy.data.scenes['Scene'].render.film_transparent = 1
#bpy.data.scenes['Scene'].render.resolution_x = 1024
#bpy.data.scenes['Scene'].render.resolution_y = 1024
#bpy.data.scenes['Scene'].render.resolution_percentage = 100
#bpy.data.scenes['Scene'].render.filepath = '/Users/clowder/Documents/research/solview/plt/solar.png'
#bpy.ops.render.render(write_still=True)

# ffmpeg -framerate 24 -i /tmp/%04d.png -vcodec libx264 -vf scale=1280:-2,format=yuv420p -q 0 ~/Downloads/solanimate.mp4
