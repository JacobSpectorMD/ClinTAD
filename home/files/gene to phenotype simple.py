output = open('genes_to_phenotypes_weighted.txt', 'w')
current_gene = 'CLPP'
output.write('CLPP' + '\t')

with open('weighted.txt', 'r') as f:
    for line in f:
        line_text = line.split("\t")
        if (line_text[1] == current_gene):
            output.write(line_text[3].strip() + 'w' + line_text[4].strip()+', ')
        if (line_text[1] != current_gene):
            output.write('\n' + line_text[1].strip() + '\t' + line_text[3].strip()+ 'w' + line_text[4].strip()+ ', ')
            current_gene = line_text[1]

output.close()
f.close()
