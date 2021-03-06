import numpy as np

from cs231n.layers import *
from cs231n.fast_layers import *
from cs231n.layer_utils import *


class ThreeLayerConvNet(object):
  """
  A three-layer convolutional network with the following architecture:
  
  conv - relu - 2x2 max pool - affine - relu - affine - softmax
  
  The network operates on minibatches of data that have shape (N, C, H, W)
  consisting of N images, each with height H and width W and with C input
  channels.
  """
  
  def __init__(self, input_dim=(3, 32, 32), num_filters=32, filter_size=7,
               hidden_dim=100, num_classes=10, weight_scale=1e-3, reg=0.0,
               dtype=np.float32):
    """
    Initialize a new network.
    
    Inputs:
    - input_dim: Tuple (C, H, W) giving size of input data
    - num_filters: Number of filters to use in the convolutional layer
    - filter_size: Size of filters to use in the convolutional layer
    - hidden_dim: Number of units to use in the fully-connected hidden layer
    - num_classes: Number of scores to produce from the final affine layer.
    - weight_scale: Scalar giving standard deviation for random initialization
      of weights.
    - reg: Scalar giving L2 regularization strength
    - dtype: numpy datatype to use for computation.
    """
    self.params = {}
    self.reg = reg
    self.dtype = dtype
    
    ############################################################################
    # TODO: Initialize weights and biases for the three-layer convolutional    #
    # network. Weights should be initialized from a Gaussian with standard     #
    # deviation equal to weight_scale; biases should be initialized to zero.   #
    # All weights and biases should be stored in the dictionary self.params.   #
    # Store weights and biases for the convolutional layer using the keys 'W1' #
    # and 'b1'; use keys 'W2' and 'b2' for the weights and biases of the       #
    # hidden affine layer, and keys 'W3' and 'b3' for the weights and biases   #
    # of the output affine layer.                                              #
    ############################################################################
    C, H, W = input_dim

    # The parameters of conv and pool are copied from the loss function below
    conv_param = {'stride': 1, 'pad': (filter_size - 1) / 2}
    pool_param = {'pool_height': 2, 'pool_width': 2, 'stride': 2}

    conv_pad = conv_param['pad']
    conv_stride = conv_param['stride']
    pool_height = pool_param['pool_height']
    pool_width = pool_param['pool_width']
    pool_stride = pool_param['stride']

    # Convolutional layer
    conv_w_shape = (num_filters, C, filter_size, filter_size)
    self.params['W1'] = weight_scale * np.random.randn(*conv_w_shape)
    self.params['b1'] = np.zeros(num_filters)

    # Hidden affine layer
    H_after_conv = 1 + (H + 2 * conv_pad - filter_size) / conv_stride
    W_after_conv = 1 + (W + 2 * conv_pad - filter_size) / conv_stride
    H_after_pool = 1 + (H_after_conv - pool_height) / pool_stride
    W_after_pool = 1 + (W_after_conv - pool_width) / pool_stride

    hidden_input_size = num_filters * H_after_pool * W_after_pool
    self.params['W2'] = weight_scale * np.random.randn(hidden_input_size,
                                                       hidden_dim)
    self.params['b2'] = np.zeros(hidden_dim)

    # Output affine layer
    self.params['W3'] = weight_scale * np.random.randn(hidden_dim, num_classes)
    self.params['b3'] = np.zeros(num_classes)
    ############################################################################
    #                             END OF YOUR CODE                             #
    ############################################################################

    for k, v in self.params.iteritems():
      self.params[k] = v.astype(dtype)
     
 
  def loss(self, X, y=None):
    """
    Evaluate loss and gradient for the three-layer convolutional network.
    
    Input / output: Same API as TwoLayerNet in fc_net.py.
    """
    W1, b1 = self.params['W1'], self.params['b1']
    W2, b2 = self.params['W2'], self.params['b2']
    W3, b3 = self.params['W3'], self.params['b3']
    
    # pass conv_param to the forward pass for the convolutional layer
    filter_size = W1.shape[2]
    conv_param = {'stride': 1, 'pad': (filter_size - 1) / 2}

    # pass pool_param to the forward pass for the max-pooling layer
    pool_param = {'pool_height': 2, 'pool_width': 2, 'stride': 2}

    scores = None
    ############################################################################
    # TODO: Implement the forward pass for the three-layer convolutional net,  #
    # computing the class scores for X and storing them in the scores          #
    # variable.                                                                #
    ############################################################################
    N, C, H, W = X.shape

    layer1_out, layer1_cache = conv_relu_pool_forward(X, W1, b1,
                                                      conv_param, pool_param)
    layer1_out_original_shape = layer1_out.shape
    layer1_out = layer1_out.reshape(N, -1)
    layer2_out, layer2_cache = affine_relu_forward(layer1_out, W2, b2)
    layer3_out, layer3_cache = affine_forward(layer2_out, W3, b3)
    scores = layer3_out
    ############################################################################
    #                             END OF YOUR CODE                             #
    ############################################################################
    
    if y is None:
      return scores
    
    loss, grads = 0, {}
    ############################################################################
    # TODO: Implement the backward pass for the three-layer convolutional net, #
    # storing the loss and gradients in the loss and grads variables. Compute  #
    # data loss using softmax, and make sure that grads[k] holds the gradients #
    # for self.params[k]. Don't forget to add L2 regularization!               #
    ############################################################################
    loss, dlayer3 = softmax_loss(layer3_out, y)
    dlayer2, dW3, db3 = affine_backward(dlayer3, layer3_cache)
    dlayer1, dW2, db2 = affine_relu_backward(dlayer2, layer2_cache)
    dlayer1 = dlayer1.reshape(*layer1_out_original_shape)
    dX, dW1, db1 = conv_relu_pool_backward(dlayer1, layer1_cache)

    loss += 0.5 * self.reg * (np.sum(W1**2) + np.sum(W2**2) + np.sum(W3**2))

    grads['W1'] = dW1 + self.reg * W1
    grads['b1'] = db1
    grads['W2'] = dW2 + self.reg * W2
    grads['b2'] = db2
    grads['W3'] = dW3 + self.reg * W3
    grads['b3'] = db3
    ############################################################################
    #                             END OF YOUR CODE                             #
    ############################################################################
    
    return loss, grads
  
  
pass
