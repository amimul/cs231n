import numpy as np

from cs231n.layers import *
from cs231n.layer_utils import *


class TwoLayerNet(object):
  """
  A two-layer fully-connected neural network with ReLU nonlinearity and
  softmax loss that uses a modular layer design. We assume an input dimension
  of D, a hidden dimension of H, and perform classification over C classes.
  
  The architecure should be affine - relu - affine - softmax.

  Note that this class does not implement gradient descent; instead, it
  will interact with a separate Solver object that is responsible for running
  optimization.

  The learnable parameters of the model are stored in the dictionary
  self.params that maps parameter names to numpy arrays.
  """
  
  def __init__(self, input_dim=3*32*32, hidden_dim=100, num_classes=10,
               weight_scale=1e-3, reg=0.0):
    """
    Initialize a new network.

    Inputs:
    - input_dim: An integer giving the size of the input
    - hidden_dim: An integer giving the size of the hidden layer
    - num_classes: An integer giving the number of classes to classify
    - dropout: Scalar between 0 and 1 giving dropout strength.
    - weight_scale: Scalar giving the standard deviation for random
      initialization of the weights.
    - reg: Scalar giving L2 regularization strength.
    """
    self.params = {}
    self.reg = reg
    
    ############################################################################
    # TODO: Initialize the weights and biases of the two-layer net. Weights    #
    # should be initialized from a Gaussian with standard deviation equal to   #
    # weight_scale, and biases should be initialized to zero. All weights and  #
    # biases should be stored in the dictionary self.params, with first layer  #
    # weights and biases using the keys 'W1' and 'b1' and second layer weights #
    # and biases using the keys 'W2' and 'b2'.                                 #
    ############################################################################
    self.params['W1'] = weight_scale * np.random.randn(input_dim, hidden_dim)
    self.params['b1'] = np.zeros(hidden_dim)
    self.params['W2'] = weight_scale * np.random.randn(hidden_dim, num_classes)
    self.params['b2'] = np.zeros(num_classes)
    ############################################################################
    #                             END OF YOUR CODE                             #
    ############################################################################


  def loss(self, X, y=None):
    """
    Compute loss and gradient for a minibatch of data.

    Inputs:
    - X: Array of input data of shape (N, d_1, ..., d_k)
    - y: Array of labels, of shape (N,). y[i] gives the label for X[i].

    Returns:
    If y is None, then run a test-time forward pass of the model and return:
    - scores: Array of shape (N, C) giving classification scores, where
      scores[i, c] is the classification score for X[i] and class c.

    If y is not None, then run a training-time forward and backward pass and
    return a tuple of:
    - loss: Scalar value giving the loss
    - grads: Dictionary with the same keys as self.params, mapping parameter
      names to gradients of the loss with respect to those parameters.
    """  
    scores = None
    ############################################################################
    # TODO: Implement the forward pass for the two-layer net, computing the    #
    # class scores for X and storing them in the scores variable.              #
    ############################################################################
    W1 = self.params['W1']
    b1 = self.params['b1']
    W2 = self.params['W2']
    b2 = self.params['b2']

    N = X.shape[0]
    X_flat = X.reshape(N, -1)
    
    fc1_out, fc1_cache = affine_forward(X_flat, W1, b1)
    relu_out, relu_cache = relu_forward(fc1_out)
    fc2_out, fc2_cache = affine_forward(relu_out, W2, b2)

    scores = fc2_out
    ############################################################################
    #                             END OF YOUR CODE                             #
    ############################################################################

    # If y is None then we are in test mode so just return scores
    if y is None:
      return scores
    
    loss, grads = 0, {}
    ############################################################################
    # TODO: Implement the backward pass for the two-layer net. Store the loss  #
    # in the loss variable and gradients in the grads dictionary. Compute data #
    # loss using softmax, and make sure that grads[k] holds the gradients for  #
    # self.params[k]. Don't forget to add L2 regularization!                   #
    #                                                                          #
    # NOTE: To ensure that your implementation matches ours and you pass the   #
    # automated tests, make sure that your L2 regularization includes a factor #
    # of 0.5 to simplify the expression for the gradient.                      #
    ############################################################################
    loss, dfc2 = softmax_loss(fc2_out, y)
    drelu, dW2, db2 = affine_backward(dfc2, fc2_cache)
    dfc1 = relu_backward(drelu, relu_cache)
    dX, dW1, db1 = affine_backward(dfc1, fc1_cache)

    loss += 0.5 * self.reg * (np.sum(W1**2) + np.sum(W2**2))

    grads['W1'] = dW1 + self.reg * W1
    grads['b1'] = db1
    grads['W2'] = dW2 + self.reg * W2
    grads['b2'] = db2
    ############################################################################
    #                             END OF YOUR CODE                             #
    ############################################################################

    return loss, grads


class FullyConnectedNet(object):
  """
  A fully-connected neural network with an arbitrary number of hidden layers,
  ReLU nonlinearities, and a softmax loss function. This will also implement
  dropout and batch normalization as options. For a network with L layers,
  the architecture will be
  
  {affine - [batch norm] - relu - [dropout]} x (L - 1) - affine - softmax
  
  where batch normalization and dropout are optional, and the {...} block is
  repeated L - 1 times.
  
  Similar to the TwoLayerNet above, learnable parameters are stored in the
  self.params dictionary and will be learned using the Solver class.
  """

  def __init__(self, hidden_dims, input_dim=3*32*32, num_classes=10,
               dropout=0, use_batchnorm=False, reg=0.0,
               weight_scale=1e-2, dtype=np.float32, seed=None):
    """
    Initialize a new FullyConnectedNet.
    
    Inputs:
    - hidden_dims: A list of integers giving the size of each hidden layer.
    - input_dim: An integer giving the size of the input.
    - num_classes: An integer giving the number of classes to classify.
    - dropout: Scalar between 0 and 1 giving dropout strength. If dropout=0 then
      the network should not use dropout at all.
    - use_batchnorm: Whether or not the network should use batch normalization.
    - reg: Scalar giving L2 regularization strength.
    - weight_scale: Scalar giving the standard deviation for random
      initialization of the weights.
    - dtype: A numpy datatype object; all computations will be performed using
      this datatype. float32 is faster but less accurate, so you should use
      float64 for numeric gradient checking.
    - seed: If not None, then pass this random seed to the dropout layers. This
      will make the dropout layers deteriminstic so we can gradient check the
      model.
    """
    self.use_batchnorm = use_batchnorm
    self.use_dropout = dropout > 0
    self.reg = reg
    self.num_layers = 1 + len(hidden_dims)
    self.dtype = dtype
    self.params = {}

    ############################################################################
    # TODO: Initialize the parameters of the network, storing all values in    #
    # the self.params dictionary. Store weights and biases for the first layer #
    # in W1 and b1; for the second layer use W2 and b2, etc. Weights should be #
    # initialized from a normal distribution with standard deviation equal to  #
    # weight_scale and biases should be initialized to zero.                   #
    #                                                                          #
    # When using batch normalization, store scale and shift parameters for the #
    # first layer in gamma1 and beta1; for the second layer use gamma2 and     #
    # beta2, etc. Scale parameters should be initialized to one and shift      #
    # parameters should be initialized to zero.                                #
    ############################################################################
    for i in range(self.num_layers):
      layer_input_size = input_dim if i - 1 < 0 else hidden_dims[i - 1]
      layer_output_size = (num_classes if i == self.num_layers - 1
                                       else hidden_dims[i])

      W_name = 'W' + str(i + 1)
      b_name = 'b' + str(i + 1)
      self.params[W_name] = weight_scale * np.random.randn(layer_input_size,
                                                           layer_output_size)
      self.params[b_name] = np.zeros(layer_output_size)

      if self.use_batchnorm and i < self.num_layers - 1:
        gamma_name = 'gamma' + str(i + 1)
        beta_name = 'beta' + str(i + 1)
        self.params[gamma_name] = np.ones(layer_output_size)
        self.params[beta_name] = np.ones(layer_output_size)
    ############################################################################
    #                             END OF YOUR CODE                             #
    ############################################################################

    # When using dropout we need to pass a dropout_param dictionary to each
    # dropout layer so that the layer knows the dropout probability and the mode
    # (train / test). You can pass the same dropout_param to each dropout layer.
    self.dropout_param = {}
    if self.use_dropout:
      self.dropout_param = {'mode': 'train', 'p': dropout}
      if seed is not None:
        self.dropout_param['seed'] = seed
    
    # With batch normalization we need to keep track of running means and
    # variances, so we need to pass a special bn_param object to each batch
    # normalization layer. You should pass self.bn_params[0] to the forward pass
    # of the first batch normalization layer, self.bn_params[1] to the forward
    # pass of the second batch normalization layer, etc.
    self.bn_params = []
    if self.use_batchnorm:
      self.bn_params = [{'mode': 'train'} for i in xrange(self.num_layers - 1)]
    
    # Cast all parameters to the correct datatype
    for k, v in self.params.iteritems():
      self.params[k] = v.astype(dtype)


  def loss(self, X, y=None):
    """
    Compute loss and gradient for the fully-connected net.

    Input / output: Same as TwoLayerNet above.
    """
    X = X.astype(self.dtype)
    mode = 'test' if y is None else 'train'

    # Set train/test mode for batchnorm params and dropout param since they
    # behave differently during training and testing.
    if self.dropout_param is not None:
      self.dropout_param['mode'] = mode   
    if self.use_batchnorm:
      for bn_param in self.bn_params:
        bn_param[mode] = mode

    scores = None
    ############################################################################
    # TODO: Implement the forward pass for the fully-connected net, computing  #
    # the class scores for X and storing them in the scores variable.          #
    #                                                                          #
    # When using dropout, you'll need to pass self.dropout_param to each       #
    # dropout forward pass.                                                    #
    #                                                                          #
    # When using batch normalization, you'll need to pass self.bn_params[0] to #
    # the forward pass for the first batch normalization layer, pass           #
    # self.bn_params[1] to the forward pass for the second batch normalization #
    # layer, etc.                                                              #
    ############################################################################
    num_train = X.shape[0]
    X_flat = X.reshape(num_train, -1)
    layer_input = X_flat
    layer_caches = []
    for i in range(self.num_layers):
      bn_cache, relu_cache, dp_cache = None, None, None

      W_name = 'W' + str(i + 1)
      b_name = 'b' + str(i + 1)
      W = self.params[W_name]
      b = self.params[b_name]
      fc_out, fc_cache = affine_forward(layer_input, W, b)

      if i == self.num_layers - 1:
        scores = fc_out
      else:
        if self.use_batchnorm:
          gamma_name = 'gamma' + str(i + 1)
          beta_name = 'beta' + str(i + 1)
          gamma = self.params[gamma_name]
          beta = self.params[beta_name]
          bn_out, bn_cache = batchnorm_forward(fc_out, gamma, beta,
                                               self.bn_params[i])
          relu_input = bn_out
        else:
          relu_input = fc_out

        relu_out, relu_cache = relu_forward(relu_input)

        if self.use_dropout:
          dp_out, dp_cache = dropout_forward(relu_out, self.dropout_param)
          layer_input = dp_out
        else:
          layer_input = relu_out

      layer_caches.append((fc_cache, bn_cache, relu_cache, dp_cache))
    ############################################################################
    #                             END OF YOUR CODE                             #
    ############################################################################

    # If test mode return early
    if mode == 'test':
      return scores

    loss, grads = 0.0, {}
    ############################################################################
    # TODO: Implement the backward pass for the fully-connected net. Store the #
    # loss in the loss variable and gradients in the grads dictionary. Compute #
    # data loss using softmax, and make sure that grads[k] holds the gradients #
    # for self.params[k]. Don't forget to add L2 regularization!               #
    #                                                                          #
    # When using batch normalization, you don't need to regularize the scale   #
    # and shift parameters.                                                    #
    #                                                                          #
    # NOTE: To ensure that your implementation matches ours and you pass the   #
    # automated tests, make sure that your L2 regularization includes a factor #
    # of 0.5 to simplify the expression for the gradient.                      #
    ############################################################################
    for i in reversed(range(self.num_layers)):
      fc_cache, bn_cache, relu_cache, dp_cache = layer_caches[i]

      if i == self.num_layers - 1:
        loss, dfc = softmax_loss(scores, y)
      else:
        if self.use_dropout:
          drelu = dropout_backward(doutput, dp_cache)
        else:
          drelu = doutput

        dbn_or_dfc = relu_backward(drelu, relu_cache)

        if self.use_batchnorm:
          dbn = dbn_or_dfc
          dfc, dgamma, dbeta = batchnorm_backward(dbn, bn_cache)
        else:
          dfc = dbn_or_dfc

      dinput, dW, db = affine_backward(dfc, fc_cache)

      W_name = 'W' + str(i + 1)
      b_name = 'b' + str(i + 1)
      W = self.params[W_name]
      loss += 0.5 * self.reg * np.sum(W**2)

      grads[W_name] = dW + self.reg * W
      grads[b_name] = db
      if self.use_batchnorm and i < self.num_layers - 1:
        gamma_name = 'gamma' + str(i + 1)
        beta_name = 'beta' + str(i + 1)
        grads[gamma_name] = dgamma
        grads[beta_name] = dbeta

      doutput = dinput
    ############################################################################
    #                             END OF YOUR CODE                             #
    ############################################################################

    return loss, grads
