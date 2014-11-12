#!/usr/bin/env python

# Created in: Jun 19, 2014
# Last modified in: Sep 27, 2014
# Author: Diogo Matos <dmatos88@gmail.com>
# Based on: create_tabley.py by Leandro Lima <llima@ime.usp.br>
# Using KEGG REST python API: https://pypi.python.org/pypi/keggrest/0.1.1
# Using KEGG API: http://www.kegg.jp/kegg/docs/keggapi.html

from keggrest import *
import sys, traceback

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
    
'''
Insert entries to both genes dictionary and kegg orthology dictionary given
a species code and its genes on a specific pathway.

genesDict    - Dicionario de genes {definition : {species_code : gene_code}}
genes        - possiveis chaves que vao entrar
species_code - codigo do organismo
'''
def makeGenesDict(genesDict, koDict, genes, species_code):
    for gene in genes:
        try:         
            geneTemp = gene.split('\t')[1].split(':')[1]
            defs = keggrest.RESTrequest('find/genes/'+geneTemp)
            #print defs
            defsSplited =  defs.split(';')                            
            definition = defsSplited[1] 
            if(definition.startswith(' K')):
                definition = defsSplited[0].replace(gene.split('\t')[1], '')

            if(definition.startswith('\t')):
                definition = ' '+definition[1:len(definition)]

            definition = definition.lower()                

            #print definition             
            
            koList = keggrest.RESTrequest('link/ko/'+defsSplited[0]).split('\n')[0:-1]           
            
            koCode = koList[0].split('\t')[1]
            koCode = koCode.split(':')[1]              
                        
            if ((koCode, definition) not in koDict):
                koDict[(koCode, definition)] = {}
                #genesDict[koCode] = {}
            
            if species_code not in koDict[(koCode, definition)]:
                koDict[(koCode, definition)][species_code] = []
            
            #genesDict[koCode][species_code] = gene.split('\t')[1]            
            koDict[(koCode, definition)][species_code].append(gene.split('\t')[1])
            
        except Exception:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_tb(exc_traceback)
            traceback.print_exception(exc_type, exc_value, exc_traceback)
            print ('NO DEFINITION FOUND FOR ' + gene + ' IN ' + species_code)
            
'''
Creates comparison table of organisms for a given pathway.

pathway         - pathway code
organismsNames  - list of organisms names
organisms       - list of abreviations of organisms
'''    
def pathwayComparisonTable(pathway, organismsNames, organisms, num_of_enzymes):
    print ('creating page for '+pathway)
    htmlFileName = pathway + '_comparison_table.html'
    presenceHtmlFileName = pathway + '_presence_table.html'
    html = open('../'+htmlFileName, 'w')
    presence_html = open('../'+presenceHtmlFileName, 'w')

    #gene comparison table page
    html.write('<html><head>\n')
    html.write('<title>Pathway %s</title>\n' % (pathway))    
    html.write('<script type="text/javascript" src="javascript/tablesorter-master/jquery-latest.js"></script>\n') 
    html.write('<script type="text/javascript" src="javascript/tablesorter-master/jquery.tablesorter.js"></script>\n')
    html.write('<script type="text/javascript" src="javascript/tablesorter.js"></script>\n')    
    html.write('<link rel="stylesheet" href="css/style.css" type="text/css">\n')
    html.write('</head>\n<body>\n')
    html.write('<h1 > <a href="http://www.genome.jp/kegg/pathway/map/map%s.html"> Pathway %s </a> </h1>' % (pathway, pathway))
       
    html.write('<table border="1" class="tablesorter">\n')
    html.write('<thead>\n')
    html.write('<tr><td rowspan="2"><center>Genes</center></td>\n')
    #html.write('<tr><td><center> - </center></td>\n')    

    #gene presence table page
    presence_html.write('<html><head>\n')
    presence_html.write('<title>Pathway %s</title>\n' % (pathway))    
    presence_html.write('<script type="text/javascript" src="javascript/tablesorter-master/jquery-latest.js"></script>\n') 
    presence_html.write('<script type="text/javascript" src="javascript/tablesorter-master/jquery.tablesorter.js"></script>\n')
    presence_html.write('<script type="text/javascript" src="javascript/tablesorter.js"></script>\n')    
    presence_html.write('<link rel="stylesheet" href="css/style.css" type="text/css">\n')
    presence_html.write('</head>\n<body>\n')
    presence_html.write('<h1 > <a href="http://www.genome.jp/kegg/pathway/map/map%s.html"> Pathway %s </a> </h1>' % (pathway, pathway))
       
    presence_html.write('<table border="1" class="tablesorter">\n')
    presence_html.write('<thead>\n')
    presence_html.write('<tr><td rowspan="2"><center>Genes</center></td>\n')
    
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
        presence_html.write('<td colspan="%d" bgcolor="%s">%s</td>\n' % (count, colors[i], organismsNames[i]))
    html.write('</tr>\n')
    presence_html.write('</tr>\n')
    
    #html.write('<tr><td><center> - </center></td>\n') 
    
    #dictionary ko -> species_code -> gene_code
    genesDict = {}
    #dictionary ko -> definition
    koDict = {}

    #print pathway
    colorCount = 0
    leftCounter = 0
    for i in range(len(organisms)):   
        species_code = organisms[i][14:17]
        if i == organismsCounter[colorCount] + leftCounter: 
                colorCount = colorCount + 1
                leftCounter = i
        #print colorCount
        color = colors[colorCount]
        indexOfDefinition = str(organisms[i]).find(';')
        html.write('<th bgcolor="%s"><center><a href="http://www.kegg.jp/kegg-bin/show_organism?org=%s" title="%s">%s</a> <br /><font size=1>%d</font></center></th>\n' % (color, species_code, organisms[i][indexOfDefinition+1], species_code, len(keggrest.RESTrequest('list/'+species_code).split('\n'))-1))
        presence_html.write('<th bgcolor="%s"><center><a href="http://www.kegg.jp/kegg-bin/show_organism?org=%s" title="%s">%s</a> <br /><font size=1>%d</font></center></th>\n' % (color, species_code, organisms[i][indexOfDefinition+1], species_code, len(keggrest.RESTrequest('list/'+species_code).split('\n'))-1))
        #print species_code
        genes = keggrest.RESTrequest('link/genes/'+species_code+pathway).split('\n')[0:-1] 
        #print genes                               
        if (len(genes) > 0 and len(genes[0]) > 0):
            makeGenesDict(genesDict, koDict, genes, species_code)
    html.write('</tr>\n')
    html.write('</thead>\n')
    presence_html.write('</tr>\n')
    presence_html.write('</thead>\n')
    
    html.write('<tbody>')
    presence_html.write('<tbody>')            
    
    species_counter = {}
    koCode_counter = set()
    for (koCode,definition) in koDict.keys():       
        koCode_counter.add(koCode)
        #print str((koCode,definition)) +'\n'
        html.write('<tr>\n')           
        html.write('<td>%s</td>' % (definition))
        presence_html.write('<tr>\n')           
        presence_html.write('<td>%s</td>' % (definition))
        colorCount = 0
        leftCounter = 0
        for i in range(len(organisms)):
            if i == organismsCounter[colorCount] + leftCounter: 
                colorCount = colorCount + 1
                leftCounter = i
            color = colors[colorCount]
            species_code = organisms[i][14:17]
            if species_code not in species_counter.keys():
                species_counter[species_code] = 0
            if species_code in koDict[(koCode,definition)].keys():               
                html.write('<td>')                
                if(len(koDict[(koCode,definition)][species_code]) == 1):                                                          
                    html.write('<a href="http://www.genome.jp/dbget-bin/www_bget?%s">%s</a>' % (koDict[(koCode,definition)][species_code][0], koDict[(koCode,definition)][species_code][0]))                   
                    species_counter[species_code] = species_counter[species_code] + 1
                    presence_html.write('<td bgcolor="%s" color="%s"> <center>---</center>' % (color, color))
                elif(len(koDict[(koCode,definition)][species_code]) > 1):                      
                    species_counter[species_code] = species_counter[species_code] + len(koDict[(koCode,definition)][species_code])
                    presence_html.write('<td bgcolor="%s" color="%s"> ' % (color, color))                    
                    for gene in sorted(koDict[(koCode,definition)][species_code]):                                               
                        html.write('<a href="http://www.genome.jp/dbget-bin/www_bget?%s">%s</a></br>' % (gene, gene))
                        presence_html.write('<center>---</center></br>')
                html.write('</td>');
                presence_html.write('</td>')
            else:
                html.write('<td style="min-width:100px"><center style="color:#FFFFFF">    </center></td>')
                presence_html.write('<td style="min-width:65px"><center style="color:#FFFFFF">    </center></td>')                    
        html.write('</tr>\n') 
        presence_html.write('</tr>\n') 
    html.write('</tbody>')
    html.write('<tfoot>\n<tr>')    
    html.write('<td>Totals</td>')
    presence_html.write('</tbody>')
    presence_html.write('<tfoot>\n<tr>')    
    presence_html.write('<td>Totals</td>')

    colorCount = 0
    leftCounter = 0
    for i in range(len(organisms)):
        species_code = organisms[i][14:17]
        if i == organismsCounter[colorCount] + leftCounter: 
                colorCount = colorCount + 1
                leftCounter = i
        #print colorCount
        color = colors[colorCount]
        if species_code in species_counter.keys():
            html.write('<td bgcolor="%s"><center>%d</center></td>' % (color,species_counter[species_code]))
            presence_html.write('<td bgcolor="%s"><center>%d</center></td>' % (color,species_counter[species_code]))
        else:
            html.write('<td bgcolor="%s"><center>0</center></td>' % (color))
            presence_html.write('<td bgcolor="%s"><center>0</center></td>' % (color))
    html.write('</tr>\n</tfoot>')
    html.write('</table>\n') 
    html.write('<p>Table containing %d out of a total of %d genes of the Pathway %s</p>\n' % (len(koCode_counter), num_of_enzymes, pathway)) 
    html.write('<br/>')
    html.write('<a href="%s"> See presence table </a>' % (pathway + '_presence_table.html'))
    html.write('</body>\n') 
    html.write('</html>\n') 
    html.close()
    presence_html.write('</tr>\n</tfoot>')
    presence_html.write('</table>\n') 
    presence_html.write('<p>Table containing %d out of a total of %d genes of the Pathway %s</p>\n' % (len(koCode_counter), num_of_enzymes, pathway)) 
    presence_html.write('<br/>')
    presence_html.write('<a href="%s"> See comparison table </a>' % (pathway + '_comparison_table.html'))
    presence_html.write('</body>\n') 
    presence_html.write('</html>\n') 
    #presence_html.close()
    #print pathway + '\n'
    #print str(koDict.keys()) +'\n...........\n'

        
def create_genes_def_page(species_code, genes, pathway, create_html=False):
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
        page.write('<br /><a href="index.html">Go back</a><br />\n')
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
    
    print ('creating page '+htmlFileName)
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
        html.write('<tr>\n<td><a href="%s_comparison_table.html" title="%s">%s</a> <font size=1>%d</font></td>\n' % (pathway, pathways_names[pathway], pathway, number_of_enzymes[pathway]))
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
                pagename = create_genes_def_page(species_code, genes, pathway, True)
                html.write('<td bgcolor="%s"><center><a href="%s">%d</a></center></td>' % (color, pagename, len(genes)))
            else:
                html.write('<td bgcolor="%s"><center>%d</center></td>' % (color, 0))

        html.write('</tr>\n')
        #writes pathway comparison table page
        pathwayComparisonTable(pathway, organismsNames, organisms, number_of_enzymes[pathway])
    
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
