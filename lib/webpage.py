import os
import glob

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

    main_html = header

    # Info
    main_html += '<p> Date: %s </p>' % info['date']
    main_html += '<p> Mini version: %s </p>' % info['version']
    main_html += '<p> Lumi: %.2f pb-1 </p>' % info['lumi']
    main_html += '<p> Systematics: %s (theoretical syst always used) </p>' % info['syst']

    # Yield tables
    main_html += '\n\n<p><h2> Yields tables </h2></p>\n\n'

    tables = [
        analysis_dir+'/tables/table_cr_srl_srh.html',
        analysis_dir+'/tables/table_vrm_srl_srh.html',
        analysis_dir+'/tables/table_vrl_srl_srh.html',
        analysis_dir+'/tables/table_vrd_srl_srh.html',
        analysis_dir+'/tables/table_sr_srl_srh.html',
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

    ## Regions pull
    if glob.glob(plots_dir+'/pull_regions*.png'):

        os.system('mv %s/pull_regions_SR_L_data.png %s/' % (plots_dir, webdir))
        os.system('mv %s/pull_regions_SR_H_data.png %s/' % (plots_dir, webdir))

        main_html += """
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

        main_html += '<tr>'
        main_html += '<td><a href=\"pull_regions_SR_L_data.png\"><img src=\"pull_regions_SR_L_data.png\" width=\"540\" height=\"380\"></a></td>'
        main_html += '<td><a href=\"pull_regions_SR_H_data.png\"><img src=\"pull_regions_SR_H_data.png\" width=\"540\" height=\"380\"></a></td>'
        main_html += '</tr>\n</table>\n</center><p></p>\n'
    
    ## Regions distributions
    for region in regions:
            
        plot_list  = glob.glob(plots_dir+'/can_{0}_L_*.png'.format(region))

        if not plot_list:
            continue

        main_html += "<center>"

        main_html += """

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

            main_html += '<tr>'

            plot_path = plot
            plot_name = plot.split('/')[-1] 

            os.system('mv %s %s/' % (plot_path, webdir))
        
            main_html += '<td><a href=\"' + plot_name + '\"><img src=\"' + plot_name + '\" width=\"480\" height=\"480\"></a></td>'

            plot_path = plot.replace('_L_', '_H_')
            plot_name = plot_name.replace('_L_', '_H_')

            os.system('mv %s %s/' % (plot_path, webdir))
        
            main_html += '<td><a href=\"' + plot_name + '\"><img src=\"' + plot_name + '\" width=\"480\" height=\"480\"></a></td>'
            main_html += '</tr>'
                
            main_html += "</table>"
            main_html += "</center>"


    ## More plots
    #     page.add_section('More plots')
    #     page.add('<ul> <li><a href="signal_contamination.html">Signal contamination</a></li></ul>')


    # Save html files
    with open(main_path, 'w') as f:
        f.write(main_html)




