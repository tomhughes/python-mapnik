from timeit import Timer, time
import mapnik

combinations = ['png',
                'png8',
                'png8:m=o',
                'png8:m=h',
                'png8:m=o:t=0',
                'png8:m=o:t=1',
                'png8:m=o:t=2',
                'png8:m=h:t=0',
                'png8:m=h:t=1',
                'png8:m=h:t=2',
                'png:z=1',
                'png:z=1:t=0',  # forces rbg, no a
                'png8:z=1',
                'png8:z=1:m=o',
                'png8:z=1:m=h',
                'png8:z=1:c=1',
                'png8:z=1:c=24',
                'png8:z=1:c=64',
                'png8:z=1:c=128',
                'png8:z=1:c=200',
                'png8:z=1:c=255',
                'png8:z=9:c=64',
                'png8:z=9:c=128',
                'png8:z=9:c=200',
                'png8:z=1:c=50:m=h',
                'png8:z=1:c=1:m=o',
                'png8:z=1:c=1:m=o:s=filtered',
                'png:z=1:s=filtered',
                'png:z=1:s=huff',
                'png:z=1:s=rle',
                'png8:m=h:g=2.0',
                'png8:m=h:g=1.0'
                ]

tiles = [
    'blank',
    'solid',
    'many_colors',
    'aerial_24'
]

iterations = 10


def do_encoding():

    global image

    results = {}
    sortable = {}

    def run(func, im, format, t):
        global image
        image = im
        start = time.time()
        set = t.repeat(iterations, 1)
        elapsed = (time.time() - start)
        min_ = min(set) * 1000
        avg = (sum(set) / len(set)) * 1000
        name = func.__name__ + ' ' + format
        results[name] = [min_, avg, elapsed * 1000, name, len(func())]
        sortable[name] = [min_]

    if 'blank' in tiles:
        def blank():
            return eval('image.to_string("%s")' % c)
        blank_im = mapnik.Image(512, 512)
        for c in combinations:
            t = Timer(blank)
            run(blank, blank_im, c, t)

    if 'solid' in tiles:
        def solid():
            return eval('image.to_string("%s")' % c)
        solid_im = mapnik.Image(512, 512)
        solid_im.fill(mapnik.Color("#f2efe9"))
        for c in combinations:
            t = Timer(solid)
            run(solid, solid_im, c, t)

    if 'many_colors' in tiles:
        def many_colors():
            return eval('image.to_string("%s")' % c)
        # lots of colors: http://tile.osm.org/13/4194/2747.png
        many_colors_im = mapnik.Image.open('../data/images/13_4194_2747.png')
        for c in combinations:
            t = Timer(many_colors)
            run(many_colors, many_colors_im, c, t)

    if 'aerial_24' in tiles:
        def aerial_24():
            return eval('image.to_string("%s")' % c)
        aerial_24_im = mapnik.Image.open('../data/images/12_654_1580.png')
        for c in combinations:
            t = Timer(aerial_24)
            run(aerial_24, aerial_24_im, c, t)

    for key, value in sorted(sortable.items(), key=lambda i: (i[1], i[0])):
        s = results[key]
        min_ = str(s[0])[:6]
        avg = str(s[1])[:6]
        elapsed = str(s[2])[:6]
        name = s[3]
        size = s[4]
        print(
            'min: %sms | avg: %sms | total: %sms | len: %s <-- %s' %
            (min_, avg, elapsed, size, name))
