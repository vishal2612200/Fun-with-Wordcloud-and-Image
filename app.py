from flask import Flask,render_template,request
import os,uuid
from PIL import Image

import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_gradient_magnitude

from wordcloud import WordCloud, ImageColorGenerator



app = Flask(__name__)

@app.route("/")
def index():
    return render_template('layouts/default.html',
                            content=render_template( 'pages/index.html'))

@app.route("/wordcloud",methods=["GET", "POST"])
def wordcloud():
    if request.method == "POST":
        text = request.form["inputtext"]
        image_file = request.files['imagefile']
        extension = os.path.splitext(image_file.filename)[1]
        f_name = str(uuid.uuid4()) + extension
        image_file.save(os.path.join('static/Uploads', f_name))
        print(image_file)
        # load image. This has been modified in gimp to be brighter and have more saturation.
        parrot_color = np.array(Image.open(os.path.join('static/Uploads', f_name)))
        # subsample by factor of 3. Very lossy but for a wordcloud we don't really care.
        parrot_color = parrot_color[::3, ::3]

        # create mask  white is "masked out"
        parrot_mask = parrot_color.copy()
        parrot_mask[parrot_mask.sum(axis=2) == 0] = 255

        # some finesse: we enforce boundaries between colors so they get less washed out.
        # For that we do some edge detection in the image
        edges = np.mean([gaussian_gradient_magnitude(parrot_color[:, :, i] / 255., 2) for i in range(3)], axis=0)
        parrot_mask[edges > .08] = 255

        # create wordcloud. A bit sluggish, you can subsample more strongly for quicker rendering
        # relative_scaling=0 means the frequencies in the data are reflected less
        # acurately but it makes a better picture
        wc = WordCloud(max_words=2000, mask=parrot_mask, max_font_size=40, random_state=42, relative_scaling=0)

        # generate word cloud
        wc.generate(text)
        plt.imsave('static/download/simpletext.jpg',wc)

        # create coloring from image
        image_colors = ImageColorGenerator(parrot_color)
        wc.recolor(color_func=image_colors)
        plt.figure(figsize=(10, 10))
        plt.imsave('2.jpg',wc)
        wc.to_file("static/download/finalimage.png")
        #Edge Map
        plt.figure(figsize=(10, 10))
        plt.title("Edge map")
        plt.imsave('static/download/edgeimage.png',edges)
        
    return render_template('layouts/default.html',
                            content=render_template( 'pages/showimage.html'))



if __name__ == "__main__":
    
    app.run(debug=True)
