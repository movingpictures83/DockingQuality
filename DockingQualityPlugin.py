import PyPluMA
import PyIO
import pandas as pd
import pickle
def access_capri_quality(irmsd, lrmsd, fnat):
    if fnat>=0.5 and (lrmsd<=1 or irmsd<=1):
        return 1 # high quality
    elif (fnat >= 0.5 and lrmsd > 1 and irmsd>1) or (fnat >= 0.3 and fnat<0.5 and lrmsd<=5 and irmsd<=2):
        return 2
    elif (fnat<0.1) or (lrmsd>10 and irmsd>4):
        return 4
    else:
        return 3


class DockingQualityPlugin:
 def input(self, inputfile):
       self.parameters = PyIO.readParameters(inputfile)
 def run(self):
        pass
 def output(self, outputfile):
  quality_dir = PyPluMA.prefix()+"/"+self.parameters["dockingqualities"]
  all_labels = []
  all_ppis = []
  all_irmsd = []
  all_lrmsd = []
  all_fnat = []
  complexfile = open(PyPluMA.prefix()+"/"+self.parameters["complexfile"], "rb")
  complexes_2023 = pickle.load(complexfile)

  for ppi in complexes_2023:
    pid, ch1, ch2 = ppi.split('_')
    with open(f"{quality_dir}/{ppi}_qual.csv", 'r') as f:
        f.readline()
        for line in f.readlines():
            model_i, model_ppi, irmsd, lrmsd, fnat = line.strip('\n').split(',')
            if float(fnat) >= 0.1 and (float(lrmsd) <= 10 or float(irmsd) <= 4):
                all_labels.append(1)
            else:
                all_labels.append(0)
            all_ppis.append(model_ppi)
            all_irmsd.append(float(irmsd))
            all_lrmsd.append(float(lrmsd))
            all_fnat.append(float(fnat))

  df_2023 = pd.DataFrame({"PPI": all_ppis,
                        "label": all_labels,
                        "iRMSD": all_irmsd,
                       "lRMSD": all_lrmsd,
                       "FNAT": all_fnat})


  df_2023['CAPRI_quality'] = df_2023.apply(lambda x: access_capri_quality(x['iRMSD'], x['lRMSD'], x['FNAT']), axis=1)
  print(df_2023)


  # ## Get statistics of positive-negative models

  # In[58]:


  df_2023['PID'] = df_2023['PPI'].apply(lambda x: x.split('-')[0])

  all_pids = []
  n_pos = []
  n_neg = []

  for pid in df_2023['PID'].unique():
    all_pids.append(pid)
    tmp_df = df_2023[df_2023['PID']==pid]
    n_pos.append(tmp_df['label'].sum())
    n_neg.append(len(tmp_df) - tmp_df['label'].sum())

  len_df = pd.DataFrame({"PID": all_pids, 'N_pos': n_pos, 'N_neg': n_neg})
  print(len_df)


  # In[59]:


  print(f"Total {df_2023['label'].sum()} pos and {len(df_2023) - df_2023['label'].sum()} neg")

  ofile = open(outputfile, "wb")
  pickle.dump(df_2023, ofile)
