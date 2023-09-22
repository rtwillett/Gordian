import numpy as np
import pandas as pd
import networkx as nx
import re
import json
import matplotlib.pyplot as plt
from .document_processing import DataFrameGraphProcessing

class DocumentReader:

    def __init__(self, filepath, source = None, sink = None, label = None):

        self.FILEPATH = filepath
        self.source_col = source
        self.target_col = sink
        self.label_col = label

        self.detect_filetype()


    def detect_filetype(self):
        
        self.file_ext = self.FILEPATH.split('.')[-1].lower()
        
        open_func = {
            'csv': self.read_csv,
            'xlsx': self.read_excel,
            'xls': self.read_excel,
            'json': self.read_json,
            'gephi': self.read_gephi,
            'gml': self.read_gml
        }
        
        self.df = open_func[self.file_ext]()

        if self.file_ext not in ["csv", "xlsx"]:
            pass
        else:
            if self.source_col is not None and self.target_col is not None:
            #     # if self.file_ext in ["csv", "xlsx"]:
                self.df_to_edgelist(source = self.source_col, sink = self.target_col)
            #     else: 
            #         pass
            else:
                raise Exception("Need to define a source and sink column")

    def read_csv(self, sep = ","):
        return pd.read_csv(self.FILEPATH)
    
    def read_excel(self): 
        return pd.read_excel(self.FILEPATH)
    
    def read_json(self):
        with open(self.FILEPATH, 'r') as f: 
            d = f.read()
        
        return json.loads(d)
    
    def read_gephi(self):
        raise Exception("Gephi files are not yet supported.")

    def read_gml(self):

        reader = GMLReader(self.FILEPATH)
        reader.to_dataframe()

        self.NODELIST = reader.NODELIST
        self.EDGELIST = reader.EDGELIST

        return None
    
    def df_to_edgelist(self, source, sink):
        processor = DataFrameGraphProcessing(data = self.df, source = source, sink=sink)
        processor.df_to_edgelist()

        self.NODELIST = processor.NODELIST
        self.EDGELIST = processor.EDGELIST
        
        try:
            gmlw = GMLWriter(self)
            self.gml = gmlw.df_to_gml()
        except:
            raise Exception("The GML structure could not be created")
        
    def save_gml(self):
        
        if self.gml is not None:
            f = open("test_gml.gml", "w")
            f.write(self.gml)
            f.close()
        else:
            raise Exception("There is no GML data available to save")
        
    def write_csv(self, filename, sep = ","):
        self.EDGELIST.to_csv(f'./{filename}_el.csv', index=None, sep = sep)
        self.NODELIST.to_csv(f'./{filename}_nl.csv', index=None, sep = sep)
    
    def write_excel(self, filename): 
        self.EDGELIST.to_excel(f'./{filename}_el.xlsx', index=None)
        self.NODELIST.to_excel(f'./{filename}_nl.xlsx', index=None)
    
    def to_json(self):
        import json
        
        return json.load(self.FILEPATH)
    
    def write_gephi(self):
        pass 

    def write_gml(self): 
        pass

class GMLReader:
    
    def __init__(self, filepath):
        
        self.FILEPATH = filepath
        
        self.open_gml_file(self.FILEPATH)
        
    def open_gml_file(self, filepath) -> None:
        
#         Have a check that this filepath is a GML file

        with open(filepath) as f:
            self.data = f.read()
            
        self.elements = self.data.replace('\n', '').split(']')
        
    def to_dataframe(self):
        self.build_nodelist()
        self.build_edgelist()
        
    def build_nodelist(self):
        import pandas as pd
        self.NODELIST = pd.DataFrame([self.extract_node_data(i) for i in self.extract_node_raws()], columns=["id", "label"])
        
    def build_edgelist(self):
        import pandas as pd
        self.EDGELIST = pd.DataFrame([self.extract_edge_data(i) for i in self.extract_edge_raws()], columns=["source", "target", "value"])
        
    def extract_node_raws(self) ->  list[str]:
        
        return [element.strip() for element in self.elements if 'node' in element.lower()]
 
    def extract_edge_raws(self) -> list[str]:
        
        return [element.strip() for element in self.elements if 'edge' in element.lower()]
        
    def extract_value(self, pattern:str, s:str) -> str:
        import re

        s_clean = re.sub("""["']""", "", s)

        r = re.search(pattern, s)
        return r.group(1)

    def extract_node_data(self, s:str) -> tuple[str]:
        import re

        s_clean = re.sub("""["']""", "", s)

        id_ptn = "id\s+([A-Za-z0-9]{1,})"
        label_ptn = "label\s+([A-Za-z0-9]{1,})"

        return (self.extract_value(id_ptn, s_clean), self.extract_value(label_ptn, s_clean))

    def extract_edge_data(self, s:str) -> tuple[str]:
        import re

        source_ptn = "source\s+([A-Za-z0-9]{1,})\s+"
        target_ptn = "target\s+([A-Za-z0-9]{1,})\s+"
        val_ptn = "value\s+([A-Za-z0-9]{1,})?"

        return (self.extract_value(source_ptn, s), self.extract_value(target_ptn, s), self.extract_value(val_ptn, s))
    
class GMLWriter:

    def __init__(self, reader):
        self.reader = reader

    def make_gml_nodes(self):
        tt = self.reader.NODELIST.apply(lambda x: f"""node\n  [\n    id {x['id']}\n    label "{x['label']}"\n  ]\n""", axis=1).to_list()
    #     return "graph\n[\n" + "".join([f"  {i}" for i in tt]) + "]"
        return "".join([f"  {i}" for i in tt])

    def make_gml_edges(self):
        tt = self.reader.EDGELIST.apply(lambda x: f"""edge\n  [\n    source {x[self.reader.source_col]}\n    target {x[self.reader.target_col]}\n  ]\n""", axis=1).to_list()
    #     return "graph\n[\n" + "".join([f"  {i}" for i in tt]) + "]"
        return "".join([f"  {i}" for i in tt])
    
    def df_to_gml(self):
        gml_nodes = self.make_gml_nodes()
        gml_edges = self.make_gml_edges()
        
        return "graph\n[\n" + gml_nodes + gml_edges + "]"