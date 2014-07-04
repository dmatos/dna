#!/usr/bin/env python

# Created in: Jun 19, 2014
# Last modified in: Jun 19, 2014
# Author: Diogo Matos <dmatos88@gmail.com>
# Based on: create_tabley.py by Leandro Lima <llima@ime.usp.br>
# Using KEGG REST python API: https://pypi.python.org/pypi/keggrest/0.1.1
# Using KEGG API: http://www.kegg.jp/kegg/docs/keggapi.html

from keggrest import *
import sys

#list of colors
# red = FF0000, green = 00FF00, blue = 0000FF
# yellow = FFFF00, grey = C0C0C0, purple= CCAAFF
# pink = FF0066, orange = CCAA00
colors = ['#FFaaaa', '#aaFFaa', '#CaCaCa', '#FFFFaa', '#aaaaFF', '#ccaaff', '#ffaa66', '#CCaa00']

"""
h - the heat intensity
"""
def generateHeatmapColor(h, colorIndex):
    color = '#000000'
    if colorIndex == 0:         #0 red FF0000
        color = '#FF'+4*h
    elif colorIndex == 1:       #1 green 00FF00
        color ='#'+2*h+'FF'+2*h
    elif colorIndex == 2:       #2 grey scale
        color = '#'+6*h
    elif colorIndex == 3:       #3 yellow FFFF00
        color = '#FFFF'+2*h
    elif colorIndex == 4:       #4 blue 0000FF
        color = '#'+ 4*h + 'FF'
    elif colorIndex == 5:       #5 purple CC00FF
        color = '#CC'+2*h+'FF'
    elif colorIndex == 6:       #6 pink FF0066
        color = '#FF'+2*h+'66'
    elif colorIndex == 7:       #7 orange CC0000
        color = '#CC'+2*h+'00'
    return color
        
def create_page(species_code, genes, pathway, create_html=False):
    filename = 'genes_of_' + species_code + '_in_' + pathway + '.html'    
    #print 'creating page ' + filename
    if create_html:
        page = open('../'+filename, 'w')
        page.write('<html><head><title>Genes of %s in %s</title></head>\n<body>\n' % (species_code, pathway))
        page.write('Genes<br />\n  <ul>\n')
        for gene in genes:
            try: 
                geneTemp = gene.split('\t')[1].split(':')[1]
                defs = keggrest.RESTrequest('find/genes/'+geneTemp)
                #print defs
                defsSplited =  defs.split(';')                 
                definition = defsSplited[1] 
                if(definition.startswith(' K')):
                    definition = defsSplited[0].replace(gene.split('\t')[1], '')
                #print definition               
                page.write('<li>%s - DEFINITION <a href="http://www.genome.jp/dbget-bin/www_bget?%s">%s</a></li>\n' % (gene.split('\t')[1], gene.split('\t')[1], definition))
            except:
                page.write('<li>%s - NO DEFINITION FOUND <a href="http://www.genome.jp/dbget-bin/www_bget?%s">%s</a></li>\n' % (gene, gene, gene))
        page.write('  </ul>\n')
        page.write('<br /><a href="output.html">Go back</a><br />\n')
        page.write('</body></html>')
        page.close()
    return filename


""" 
find organisms on genome
"""
def list_organisms(organismsNames):
    organisms = []
    for name in organismsNames:
        #print 'find/genome/"'+name+'"'
        for org in keggrest.RESTrequest('find/genome/"'+name+'"').split('\n')[0:-1] :
            if( org.find(' '+name) >= 0):
                organisms.append(org)
    return organisms

""" 
Xenobiotics Biodegradation and Metabolism.
pathwaysLen - number of pathwways
organismsLen - number of organisms
htmlFileName - html output file name
link - html link file name
args - list of both pathways and organisms
"""
def pathways_cross_organisms(pathwaysLen, organismsLen, htmlFileName, link, args):
    map_pathways = keggrest.RESTrequest('list/pathway/').split('\n')
    pathways = []
    organismsNames = []
    for i in range(0, pathwaysLen):
        #print args[i]
        pathways.append(args[i])
    for i in range(pathwaysLen, pathwaysLen+organismsLen):
        organismsNames.append(args[i])

    number_of_enzymes = {}
    pathways_names = {}
    for pathway in map_pathways:
        pathway_id = pathway[8:13]      
        if pathway_id in pathways:
            pathways_names[pathway_id] = pathway[14:]
            number_of_enzymes[pathway_id] = len(keggrest.RESTrequest('link/enzyme/pathway:map'+pathway_id).split('\n'))-1
            
    organisms = list_organisms(organismsNames)
    
    print 'creating page '+htmlFileName
    html = open('../'+htmlFileName, 'w')
    html.write('<html><head><title>Species</title></head>\n<body>\n')
    html.write('<table border="1">\n')
    html.write('<tr><td rowspan="2">Pathways</td>\n')
    
    organismsCounter = []
    for i in range(len(organismsNames)):
        count = 0
        #print organismsNames[i]
        for org in organisms:
            if org.find(organismsNames[i]) >= 0:                                
                count = count + 1
                #print org
        #print count
        organismsCounter.append(count)
        html.write('<td colspan="%d" bgcolor="%s">%s</td>\n' % (count, colors[i], organismsNames[i]))
    html.write('</tr>\n')
    colorCount = 0
    leftCounter = 0
    for i in range(len(organisms)):
        if i == organismsCounter[colorCount] + leftCounter: 
                colorCount = colorCount + 1
                leftCounter = i
        #print colorCount
        color = colors[colorCount]
        indexOfDefinition = str(organisms[i]).find(';')
        #print organisms[i] 
        #print indexOfDefinition       
        org_id = organisms[i][14:17]
        html.write('<td bgcolor="%s"><center><a href="http://www.kegg.jp/kegg-bin/show_organism?org=%s" title="%s">%s</a> <br /><font size=1>%d</font></center></td>\n' % (color, org_id, organisms[i][indexOfDefinition+1], org_id, len(keggrest.RESTrequest('list/'+org_id).split('\n'))-1))    
    html.write('</tr>\n')
    for pathway in pathways:
        html.write('<tr>\n<td><a href="http://www.genome.jp/kegg/pathway/map/map%s.html" title="%s">%s</a> <font size=1>%d</font></td>\n' % (pathway, pathways_names[pathway], pathway, number_of_enzymes[pathway]))
        #print pathway
        colorCount = 0
        leftCounter = 0
        for i in range(len(organisms)):
            species_code = organisms[i][14:17]
            #print species_code
            genes = keggrest.RESTrequest('link/genes/'+species_code+pathway).split('\n')[0:-1] 
            #print genes            
            if i == organismsCounter[colorCount]+leftCounter: 
                colorCount = colorCount + 1
                leftCounter = i
            if htmlFileName == 'index.html':        
                h = str(hex(14*(30-len(genes))/30))[2] # calculating the color
                color = generateHeatmapColor(h, colorCount)
            else:
                color = colors[colorCount]
            if (len(genes) > 0 and len(genes[0]) > 0):
                pagename = create_page(species_code, genes, pathway, True)
                html.write('<td bgcolor="%s"><center><a href="%s">%d</a></center></td>' % (color, pagename, len(genes)))
            else:
                html.write('<td bgcolor="%s"><center>%d</center></td>' % (color, 0))

        html.write('</tr>\n')
    
    if link=='commoncolors.html':
        html.write('</table>\n<br /><a href="%s">See common colors</a>\n</body>\n</html>\n' % (link))
    else:
        html.write('</table>\n<br /><a href="%s">See heatmap</a>\n</body>\n</html>\n' % (link))
    html.close()
    return htmlFileName
    
if __name__ == "__main__":
    inputFileName = sys.argv[1]
    inputFile = open(inputFileName, 'r')
    input_ = inputFile.readlines()[0][0:-1].split(' ')    
    pathwaysLen = int(input_[0])
    organismsLen = int(input_[1])
    pathsAndOrgs = input_[2:]
    #print pathwaysLen
    #print organismsLen
    #print len(pathsAndOrgs)
    #print pathsAndOrgs
    output = 'index.html'
    link = 'commoncolors.html'    
    pathways_cross_organisms(pathwaysLen, organismsLen, output, link, pathsAndOrgs)
    output = 'commoncolors.html'
    link = 'index.html'
    pathways_cross_organisms(pathwaysLen, organismsLen, output, link, pathsAndOrgs)
    exit()
