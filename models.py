import torch.nn as nn
import torch.nn.utils.spectral_norm as SN



def conv_block(in_channels, out_channels, kernel_size, stride, padding=1, bias=True, activation=nn.ReLU(), transpose=False, no_BN=False, all_tanh=False, spec_norm=False):

    if(transpose):
        block = [nn.ConvTranspose2d(in_channels=in_channels, out_channels=out_channels, 
                                stride=stride, kernel_size=kernel_size, padding=padding, bias=bias) ]
    else:
        block = [nn.Conv2d(in_channels=in_channels, out_channels=out_channels, 
                                stride=stride, kernel_size=kernel_size, padding=padding, bias=bias) ]
        
    if(spec_norm):
        block[0] = SN(block[0])
    elif(not no_BN): 
        block.append(nn.BatchNorm2d(num_features=out_channels))

        
    if(all_tanh):
        block.append(nn.Tanh())
    elif(activation != None):
        block.append(activation)

    return block




class StandartCNN_Generator(nn.Module):

    def __init__(self, no_BN=False, all_tanh=False):
        super(StandartCNN_Generator, self).__init__()

        self.linear = nn.Sequential(nn.Flatten(), nn.Linear(128, 512*4*4))

        self.model = nn.Sequential( *conv_block(in_channels=512, out_channels=256, stride=2, kernel_size=4,
                                                transpose=True, no_BN=no_BN, all_tanh=all_tanh),

                                    *conv_block(in_channels=256, out_channels=128,  stride=2, kernel_size=4,
                                                transpose=True, no_BN=no_BN, all_tanh=all_tanh),

                                    *conv_block(in_channels=128, out_channels=64,  stride=2, kernel_size=4,
                                                transpose=True, no_BN=no_BN, all_tanh=all_tanh),

                                    *conv_block(in_channels=64, out_channels=3,  stride=1, kernel_size=3,
                                                transpose=True, no_BN=True, all_tanh=True)  )


    def forward(self, z):

        linear = self.linear(z)

        reshaped = linear.view(-1,512,4,4)

        return self.model(reshaped)



class StandartCNN_Discriminator(nn.Module):

    def __init__(self, no_BN, all_tanh, spec_norm=True):
        super(StandartCNN_Discriminator, self).__init__()


        self.model = nn.Sequential( *conv_block(in_channels=3, out_channels=64, stride=1, no_BN=no_BN,
                                                kernel_size=3, spec_norm=spec_norm, all_tanh=all_tanh,
                                                activation= nn.LeakyReLU(negative_slope=1e-1)),

                                    *conv_block(in_channels=64, out_channels=64, stride=2, no_BN=no_BN,
                                                kernel_size=4, spec_norm=spec_norm, all_tanh=all_tanh,
                                                activation= nn.LeakyReLU(negative_slope=1e-1)),

                                    *conv_block(in_channels=64, out_channels=128, stride=1, no_BN=no_BN,
                                                kernel_size=3, spec_norm=spec_norm, all_tanh=all_tanh,
                                                activation= nn.LeakyReLU(negative_slope=1e-1)),

                                    *conv_block(in_channels=128, out_channels=128, stride=2, no_BN=no_BN,
                                                kernel_size=4, spec_norm=spec_norm, all_tanh=all_tanh,
                                                activation= nn.LeakyReLU(negative_slope=1e-1)),

                                    *conv_block(in_channels=128, out_channels=256, stride=1, no_BN=no_BN,
                                                kernel_size=3, spec_norm=spec_norm, all_tanh=all_tanh,
                                                activation= nn.LeakyReLU(negative_slope=1e-1)),

                                    *conv_block(in_channels=256, out_channels=256, stride=2, no_BN=no_BN,
                                                kernel_size=4, spec_norm=spec_norm, all_tanh=all_tanh,
                                                activation= nn.LeakyReLU(negative_slope=1e-1)),
                                    
                                    *conv_block(in_channels=256, out_channels=512, stride=1, no_BN=no_BN,
                                                kernel_size=3, spec_norm=spec_norm, all_tanh=all_tanh, 
                                                activation=nn.LeakyReLU(negative_slope=1e-1)),

                                    nn.Flatten(),

                                    ( SN(nn.Linear(512*4*4, 1)) if spec_norm 
                                      else nn.Linear(512*4*4, 1))  )

    def forward(self, x):

        return self.model(x)



class DCGAN_64_Generator(nn.Module):

    def __init__(self, no_BN=False, all_tanh=False):
        super(DCGAN_64_Generator, self).__init__()


        self.model = nn.Sequential( *conv_block(in_channels=128, out_channels=512, stride=1, bias=False, padding=0,
                                                transpose=True, kernel_size=4, no_BN=no_BN, all_tanh=all_tanh),

                                    *conv_block(in_channels=512, out_channels=256, stride=2, bias=False,
                                                transpose=True, kernel_size=4, no_BN=no_BN, all_tanh=all_tanh),

                                    *conv_block(in_channels=256, out_channels=128, stride=2, bias=False,
                                                transpose=True, kernel_size=4, no_BN=no_BN, all_tanh=all_tanh),

                                    *conv_block(in_channels=128, out_channels=64, stride=2, bias=False,
                                                transpose=True, kernel_size=4, no_BN=no_BN, all_tanh=all_tanh),

                                    *conv_block(in_channels=64, out_channels=3, stride=2, bias=False,
                                                transpose=True, kernel_size=4, no_BN=True, all_tanh=True)  )

    def forward(self, z):

        return self.model(z)


class DCGAN_64_Discriminator(nn.Module):

    def __init__(self, no_BN, all_tanh, spec_norm=False):
        super(DCGAN_64_Discriminator, self).__init__()


        self.model = nn.Sequential( *conv_block(in_channels=3, out_channels=64, stride=2, no_BN=True,
                                                kernel_size=4, bias=False, all_tanh=all_tanh, spec_norm=spec_norm,
                                                activation= nn.LeakyReLU(negative_slope=2e-1)),

                                    *conv_block(in_channels=64, out_channels=128, stride=2, no_BN=no_BN,
                                                kernel_size=4, bias=False, all_tanh=all_tanh, spec_norm=spec_norm,
                                                activation= nn.LeakyReLU(negative_slope=2e-1)),

                                    *conv_block(in_channels=128, out_channels=256, stride=2, no_BN=no_BN,
                                                kernel_size=4, bias=False, all_tanh=all_tanh, spec_norm=spec_norm,
                                                activation= nn.LeakyReLU(negative_slope=2e-1)),

                                    *conv_block(in_channels=256, out_channels=512, stride=2, no_BN=no_BN,
                                                kernel_size=4, bias=False, all_tanh=all_tanh, spec_norm=spec_norm,
                                                activation= nn.LeakyReLU(negative_slope=2e-1)),
                                   
                                    *conv_block(in_channels=512, out_channels=1, stride=2, no_BN=True,
                                                kernel_size=4, bias=False, all_tanh=False, spec_norm=spec_norm,
                                                activation=None)  )

                                    
    def forward(self, x):

        return self.model(x)