# Author: Pan Yang (panyangnlp@gmail.com)
# Copyright 2017

from __future__ import print_function

import logging
import os
import sys
import multiprocessing

from gensim.models import Word2Vec
from gensim.models.word2vec import LineSentence

if __name__ == '__main__':
    program = os.path.basename(sys.argv[0])
    logger = logging.getLogger(program)

    logging.basicConfig(format='%(asctime)s: %(levelname)s: %(message)s')
    logging.root.setLevel(level=logging.INFO)
    logger.info("running %s" % ' '.join(sys.argv))

    # check and process input arguments
    if len(sys.argv) < 4:
        print("Useing: python train_word2vec_model.py input_text "
              "output_gensim_model output_word_vector")
        sys.exit(1)
    inp, outp1, outp2 = sys.argv[1:4]

    # model = Word2Vec(LineSentence(inp), size=200, window=5, min_count=1,
    #                  workers=multiprocessing.cpu_count())

    # model.save(outp1)
    # model.wv.save_word2vec_format(outp2, binary=False)
    # 增量训练
    model = Word2Vec.load(outp1)
    more_sentences = LineSentence(inp)
    model.build_vocab(more_sentences, update=True)
    model.train(more_sentences, total_examples=model.corpus_count, epochs=model.iter)
    model.save(outp1)
    model.wv.save_word2vec_format(outp2, binary=False)
