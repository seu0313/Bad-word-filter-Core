from keras.callbacks import ModelCheckpoint, EarlyStopping
from keras.models import Model, load_model, Sequential
from keras.layers import Dense, Activation, Dropout, Input, Masking, TimeDistributed, LSTM, Conv1D
from keras.layers import GRU, Bidirectional, BatchNormalization, Reshape
from keras.optimizers import Adam, SGD, RMSprop
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os

def model(input_shape):
    
    X_input = Input(shape = input_shape)
    
    X = Conv1D(196, kernel_size=15, strides=4)(X_input)   
    X = BatchNormalization()(X)                           
    X = Activation('relu')(X)                            
    X = Dropout(0.8)(X)                                   

    X = GRU(units = 128, return_sequences = True)(X) 
    X = Dropout(0.8)(X)                                   
    X = BatchNormalization()(X)                           
    
    X = GRU(units = 128, return_sequences = True)(X) 
    X = Dropout(0.8)(X)                                   
    X = BatchNormalization()(X)                           
    X = Dropout(0.8)(X)                                   

    X = TimeDistributed(Dense(1, activation = "sigmoid"))(X)

    model = Model(inputs = X_input, outputs = X)
    
    return model

def model_2(input_shape):
    
    X_input = Input(shape = input_shape)

    X = Conv1D(64, kernel_size=12, strides=4)(X_input)   
    X = BatchNormalization()(X)                           
    X = Activation('elu')(X)     

    X = Conv1D(128, kernel_size=8, strides=1, padding='same')(X)  
    X = BatchNormalization()(X) 
    X = Activation('elu')(X)                          
    X = Dropout(0.2)(X)                                   

    X = Conv1D(256, kernel_size=8, strides=1, padding='same')(X) 
    X = BatchNormalization()(X) 
    X = Activation('elu')(X)                          
    X = Dropout(0.2)(X)    

    X = LSTM(256, return_sequences= True)(X)
    X = BatchNormalization()(X)                       
    X = Dropout(0.2)(X)                                  

    X = TimeDistributed(Dense(3, activation = "softmax"))(X)

    model = Model(inputs = [X_input], outputs = [X])
    
    return model

def model_train(model, 
                X, Y, X_val, Y_val, X_dev, Y_dev,
                filename,
                opt_name='Adam',
                batch_size=5,
                epochs=30,
                validation_split=0.1,
                use_custom_valid=False):

    MODEL_SAVE_FOLDER_PATH = './model/Checkpoint/'
    if not os.path.exists(MODEL_SAVE_FOLDER_PATH):
        os.mkdir(MODEL_SAVE_FOLDER_PATH)

    model_path = MODEL_SAVE_FOLDER_PATH + 'check.h5' 
    cb_checkpoint = ModelCheckpoint(filepath=model_path, monitor='val_loss', verbose=0, save_best_only=True)
    early_stopping = EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True) # 조기종료 콜백함수 정의

    if opt_name.upper() == 'SGD':
        opt = SGD(lr=0.01, decay=1e-6, momentum=0.9, nesterov=True)
    elif opt_name.upper() == 'ADAM': # keras.io default adam
        opt = Adam(lr=0.001, beta_1=0.9, beta_2=0.999)
    elif opt_name.upper() == 'ADAM2':
        opt = Adam(lr=0.0001, beta_1=0.9, beta_2=0.999, decay=0.01)
    elif opt_name.upper() == 'RMSPROP':
        opt = RMSprop(learning_rate = 0.01)

    model.compile(loss='sparse_categorical_crossentropy', optimizer=opt, metrics=["accuracy"])

    if use_custom_valid :
        hist = model.fit(X, Y, batch_size=batch_size, epochs=epochs, validation_data=(X_val, Y_val), callbacks=[early_stopping, cb_checkpoint])
    else :
        hist = model.fit(X, Y, batch_size=batch_size, epochs=epochs, validation_split=validation_split, callbacks=[early_stopping, cb_checkpoint])
    
    print(f"{filename} loss, acc :")
    loss, acc = model.evaluate(X_dev, Y_dev)
    print(f"{filename} Dev set loss = ", loss)
    print(f"{filename} Dev set accuracy = ", acc)
    print("\n")

    model.save('./model/' + filename)

    return hist

def plot_training_accuracy(hist):

    pd.DataFrame(hist.history).plot()
    plt.grid(True)
    plt.gca().set_ylim(0,1)
    plt.show()

# 잘못 사용한 코드 (사용금지) : Don't use it
# def online_learning(Tx, n_freq,
#                     X_val, Y_val,
#                     X_dev, Y_dev,
#                     file_nums,
#                     opt_name='Adam',
#                     batch_size=5,
#                     epochs=30,
#                     validation_split=0.1,
#                     use_custom_valid=False):

#     # Online learning 방식
#     # file_nums = ['1','2','3','4','5']
    
#     hists = []
#     for file_num in file_nums :
#         X = np.load(f"./XY_file/train/X_{file_num}.npy")
#         Y = np.load(f"./XY_file/train/Y_{file_num}.npy")

#         if file_num == file_nums[0] and not os.path.exists(f'./model/olo_{file_num}.h5'):
#             model = model_2(input_shape = (Tx, n_freq))
#             model.summary()

#         elif file_num == file_nums[0] and os.path.exists(f'./model/olo_{file_num}.h5'):
#             model = load_model(f'./model/olo_{file_nums[-1]}.h5')
        
#         hist = model_train(model, X, Y, X_val, Y_val, X_dev, Y_dev, f'olo_{file_num}.h5', opt_name=opt_name, batch_size=batch_size, epochs=epochs, validation_split= validation_split, use_custom_valid=use_custom_valid)
#         hists.append(hist)

#     return hists