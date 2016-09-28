# www utils

import os
import glob

class WebPage:

    def __init__(self, webdir, title):
        self.path = os.path.join(webdir, 'index.html')
        self.title = title
        self.buffer = ''
        self.webdir = webdir


    def add(self, text):
        self.buffer += '<p>' + text + '</p>\n'
        
    def add_section(self, name):
        self.buffer += '\n\n<p><h2> %s </h2></p>\n\n' % name

    def add_file(self, fname, label):
        name = os.path.basename(fname)
        self.add('<a class=\"btn\" href=\"' + name + '\">' + label + '</a>\n')

    def add_file_text(self, path):
        self.add(open(path).read())

        # name = os.path.basename(fname)
        # self.add('<a class=\"btn\" href=\"' + name + '\">' + label + '</a>\n')

    def add_yields_table(self, path):
        table = open(path).read()
        table = table.replace('<table>', '<table class="yieldstable">')
        self.buffer += '<center>\n'
        self.buffer += table
        self.buffer += '</center>\n<p></p>\n'

    def add_plots_table(self, regions, plots_dir):

        if glob.glob(plots_dir+'/pull_regions*.png'):

            os.system('mv %s/pull_regions_SR_L_data.png %s/' % (plots_dir, self.webdir))
            os.system('mv %s/pull_regions_SR_H_data.png %s/' % (plots_dir, self.webdir))

            self.buffer += """
<center>
<table class="plotstable">
<tr>
<th colspan=2 text><h2>Pulls</h2></td>
</tr>
<tr>
<th>L</th>
<th>H</th>
</tr>
"""

            self.buffer += '<tr>'
            self.buffer += '<td><a href=\"pull_regions_SR_L_data.png\"><img src=\"pull_regions_SR_L_data.png\" width=\"540\" height=\"380\"></a></td>'
            self.buffer += '<td><a href=\"pull_regions_SR_H_data.png\"><img src=\"pull_regions_SR_H_data.png\" width=\"540\" height=\"380\"></a></td>'
            self.buffer += '</tr>\n</table>\n</center><p></p>\n'

            
        for region in regions:
            
            plot_list  = glob.glob(plots_dir+'/can_{0}_L_*.png'.format(region))
            print plot_list
            self.buffer += "<center>"

            self.buffer += """

<table class="plotstable">
<tr>
<th colspan=2 text><h2>{0}</h2></td>
</tr>
<tr>
<th>L</th>
<th>H</th>
</tr>
""".format(region)

            for plot in sorted(plot_list):

                self.buffer += '<tr>'

                plot_path = plot
                plot_name = plot.split('/')[-1] 

                os.system('mv %s %s/' % (plot_path, self.webdir))
        
                self.buffer += '<td><a href=\"' + plot_name + '\"><img src=\"' + plot_name + '\" width=\"480\" height=\"480\"></a></td>'

                plot_path = plot.replace('_L_', '_H_')
                plot_name = plot_name.replace('_L_', '_H_')

                os.system('mv %s %s/' % (plot_path, self.webdir))
        
                self.buffer += '<td><a href=\"' + plot_name + '\"><img src=\"' + plot_name + '\" width=\"480\" height=\"480\"></a></td>'
                self.buffer += '</tr>'
                
            self.buffer += "</table>"
            self.buffer += "</center>"
        


    def build_header(self):
        header = """<!DOCTYPE html>
<html>
<head>
    <title> %s </title>
    <meta charset=\"utf-8\" />
    <meta http-equiv=\"content-type\" content=\"text/html; charset=UTF-8\" />
    <link rel=\"stylesheet\" type=\"text/css\" href=\"../style.css\" />
    <script type="text/javascript" src="../yieldstable.js"> </script>
</head>

<body>
    <header class=\"clearfix page\">
        <span class=\"title\"> %s </span>
    </header>
""" % (self.title, self.title)

        return header

    def build_footer(self):
        return """
    </body>
</html>
"""

    def save(self):
        with open(self.path, 'w') as f:
            f.write(self.build_header())
            f.write(self.buffer)
            f.write(self.build_footer())




