import torch.utils.data as data
import os, sys
import argparse
import networkx as nx

reader_folder = os.path.realpath(os.path.abspath('../GraphReader'))
if reader_folder not in sys.path:
    sys.path.insert(1, reader_folder)

from GraphReader.graph_reader import read_2cols_set_files, create_numeric_classes, read_cxl, create_graph_grec

__author__ = "Pau Riba, Anjan Dutta"
__email__ = "priba@cvc.uab.cat, adutta@cvc.uab.cat"


class GREC(data.Dataset):
    def __init__(self, root_path, ids, classes, max_class_num):
        self.root = root_path
        self.subdir = 'data'
        self.classes = classes
        self.ids = ids
        self.max_class_num = max_class_num

    def __getitem__(self, index):
        g = create_graph_grec(os.path.join(self.root, self.subdir, self.ids[index]))
        target = self.classes[index]
        h = self.vertex_transform(g)
        g, e = self.edge_transform(g)
        target = self.target_transform(target)
        return (g, h, e), target

    def __len__(self):
        return len(self.ids)

    def target_transform(self, target):
        return [int(target)]  # A=65

    def vertex_transform(self, g):
        h = []
        for n, d in g.nodes_iter(data=True):
            h_t = []
            h_t += [float(x) for x in d['labels']]
            h.append(h_t)
        return h

    def edge_transform(self, g):
        e = {}
        for n1, n2, d in g.edges_iter(data=True):
            e_t = []
            e_t += [float(x) for x in list(d.values())]
            e[(n1, n2)] = e_t
        return nx.to_numpy_matrix(g), e


if __name__ == '__main__':
    # Parse optios for downloading
    parser = argparse.ArgumentParser(description='GREC Object.')
    # Optional argument
    parser.add_argument('--root', nargs=1, help='Specify the data directory.',
                        default=['/home/adutta/Workspace/Datasets/Graphs/GREC'])

    args = parser.parse_args()
    root = args.root[0]

    train_classes, train_ids = read_cxl(os.path.join(root, 'data/train.cxl'))
    test_classes, test_ids = read_cxl(os.path.join(root, 'data/test.cxl'))
    valid_classes, valid_ids = read_cxl(os.path.join(root, 'data/valid.cxl'))

    num_classes = len(list(set(train_classes+valid_classes+test_classes)))

    data_train = GREC(root, train_ids, train_classes, num_classes)
    data_valid = GREC(root, valid_ids, valid_classes, num_classes)
    data_test = GREC(root, test_ids, test_classes, num_classes)

    print(len(data_train))
    print(len(data_valid))
    print(len(data_test))

    for i in range(1000):
        print(data_train[i])
    print(data_valid[1])
    print(data_test[1])
