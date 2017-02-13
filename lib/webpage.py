import os
import glob

import regions as regions_

header = """<!DOCTYPE html>
<html>
<head>
    <title> Photon + jets + MET analysis </title>
    <meta charset=\"utf-8\" />
    <meta http-equiv=\"content-type\" content=\"text/html; charset=UTF-8\" />
    <link rel=\"stylesheet\" type=\"text/css\" href=\"../style.css\" />
    <script type="text/javascript" src="../yieldstable.js"> </script>
</head>

<body>
    <header class=\"clearfix page\">
        <span class=\"title\"> Photon + jets + MET analysis </span>
    </header>
""" 

footer = """
    </body>
</html>
"""

def create_webpage(analysis_dir, webdir, info, regions=[]):
    
    tables_dir = '%s/tables' % analysis_dir
    plots_dir  = '%s/plots' % analysis_dir

    main_path = os.path.join(webdir, 'index.html')

    main_html = ''

    # Info
    main_html += '<div class="info">\n'
    main_html += '<ul>\n'
    main_html += '<li> Date: %s </li>' % info['date']
    main_html += '<li> Mini version: %s </li>' % info['version']
    main_html += '<li> Lumi: %.2f pb-1 </li>' % info['lumi']
    main_html += '<li> Systematics: %s (theoretical syst always used) </li>' % info['syst']
    main_html += '</ul>\n'
    main_html += '</div>\n\n'

    # Yield tables
    main_html += '\n\n<p><h2> Yields tables </h2></p>\n\n'

    tables = [
        analysis_dir+'/tables/table_cr.html',
        analysis_dir+'/tables/table_vrm.html',
        analysis_dir+'/tables/table_vrl.html',
        analysis_dir+'/tables/table_vrlwt.html',
        analysis_dir+'/tables/table_sr.html',
        ]

    for table in tables:
        if not os.path.isfile(table):
            continue

        table_content = open(table).read()
        table_content = table_content.replace('<table>', '<table class="yieldstable">')

        main_html += '<center>\n'
        main_html += table_content
        main_html += '</center>\n<p></p>\n'

    
    # Plots
    main_html += '\n\n<p><h2> Plots </h2></p>\n\n'

     #pull_regions.pdf
     ## Regions pull
    if glob.glob(plots_dir+'/pull_regions.png'):

        os.system('mv %s/pull_regions.png %s/' % (plots_dir, webdir))

        main_html += '\n<center>\n'
        main_html += '<a href=\"pull_regions.png\"><img src=\"pull_regions.png\" width=\"540\" height=\"380\"></a></td>\n'
        main_html += '</center><p></p>\n'
    
    ## Regions distributions
    for region in regions:
            
        plot_list  = glob.glob(plots_dir+'/can_{0}_*.png'.format(region))

        if not plot_list:
            continue

        chunks = [plot_list[x:x+3] for x in xrange(0, len(plot_list), 3)]

        main_html += """
<center>
<h3>%s</h3>
<table class="plotstable">
""" % region

        for plots in sorted(chunks):

            main_html += '<tr>\n'

            for plot in plots:

                plot_path = plot
                plot_name = plot.split('/')[-1] 

                os.system('mv %s %s/' % (plot_path, webdir))
        
                main_html += '<td><a href=\"' + plot_name + '\"><img src=\"' + plot_name + '\" width=\"480\" height=\"480\"></a></td>\n'

            main_html += '</tr>\n'
                
        main_html += "</table>\n</center>\n"


    ## More plots
    # main_html += '\n\n<p><h2> More plots </h2></p>\n\n'

#     ### Signal contamination
#     sc_html = ''
#     for region in regions:
            
#         sc_plot  = plots_dir+'/signal_contamination_{0}_L.png'.format(region)

#         if not os.path.isfile(sc_plot):
#             continue

#         sc_html += "<center>"

#         sc_html += """

# <table class="plotstable">
# <tr>
# <th colspan=2 text><h3>{0}</h3></td>
# </tr>
# <tr>
# <th>L</th>
# <th>H</th>
# </tr>
# """.format(region)

#         sc_html += '<tr>\n'

#         plot_path = sc_plot
#         plot_name = sc_plot.split('/')[-1] 

#         os.system('mv %s %s/' % (plot_path, webdir))
        
#         sc_html += '<td><a href=\"' + plot_name + '\"><img src=\"' + plot_name + '\" width=\"540\" height=\"480\"></a></td>\n'

#         plot_path = plot_path.replace('_L', '_H')
#         plot_name = plot_name.replace('_L', '_H')

#         os.system('mv %s %s/' % (plot_path, webdir))
        
#         sc_html += '<td><a href=\"' + plot_name + '\"><img src=\"' + plot_name + '\" width=\"540\" height=\"480\"></a></td>\n'
#         sc_html += '</tr>\n'
                
#         sc_html += "</table>\n</center>\n"

#     if sc_html:
#         sc_path = os.path.join(webdir, 'signal_contamination.html')
#         with open(sc_path, 'w') as f:
#             f.write(header+sc_html+footer)

#         main_html += '<ul> <li><a href="signal_contamination.html">Signal contamination</a></li></ul>'


    # Save html files
    with open(main_path, 'w') as f:
        f.write(header+main_html+footer)




