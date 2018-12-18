from collections import Counter

output = open('hpo_weights.txt', 'w')

counts = Counter()

with open('genes_to_phenotypes.txt', 'r') as f:
    for line in f:
        line_text = line.split("\t")
        hpo = line_text[3].strip()
        counts[hpo]+=1
        
    for key, val in counts.items():
        hpo_id = int(key.split(':')[1])
        hpo_weight = 20/val
        output.write(str(hpo_id)+'\t'+str(hpo_weight)+'\n')

    # f.seek(0,0)
    # for line in f:
    #     line_text = line.split("\t")
    #     output.write(line_text[0]+'\t'+line_text[1]+'\t'+line_text[2]+'\t'+str(line_text[3].strip()))
    #     output.write("\t"+str(counts[line_text[3].strip()])+"\n")

output.close()
f.close()
            