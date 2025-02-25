# 卷积神经网络（Convolutional Neural Networks, CNN）
'''
应用范围：计算机视觉，自然语言处理NLP
'''
# 参考'https://baike.baidu.com/item/卷积神经网络'
'''
卷积神经网络（Convolutional Neural Networks, CNN）
是一类包含卷积计算且具有深度结构的前馈神经网络（Feedforward Neural Networks），
是深度学习（deep learning）的代表算法之一 。
卷积神经网络具有表征学习（representation learning）能力，
能够按其阶层结构对输入信息进行平移不变分类（shift-invariant classification），
因此也被称为“平移不变人工神经网络（Shift-Invariant Artificial Neural Networks, SIANN）”。
对卷积神经网络的研究始于二十世纪80至90年代，时间延迟网络和LeNet-5是最早出现的卷积神经网络；
在二十一世纪后，随着深度学习理论的提出和数值计算设备的改进，卷积神经网络得到了快速发展，
并被应用于计算机视觉、自然语言处理等领域 。
卷积神经网络仿造生物的视知觉（visual perception）机制构建，可以进行监督学习和非监督学习，
其隐含层内的卷积核参数共享和层间连接的稀疏性使得卷积神经网络能够以较小的计算量对格点化（grid-like topology）特征，
例如像素和音频进行学习、有稳定的效果且对数据没有额外的特征工程（feature engineering）要求。
'''

import torch 
import torch.nn as nn
import torchvision
import torchvision.transforms as transforms


# Device configuration
# 设备配置
device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')

# Hyper parameters
# 超参数
num_epochs = 5
num_classes = 10
batch_size = 100
learning_rate = 0.001

# MNIST dataset
# MNIST 数据集
train_dataset = torchvision.datasets.MNIST(root='../../data/',
                                           train=True, 
                                           transform=transforms.ToTensor(),
                                           download=True)

test_dataset = torchvision.datasets.MNIST(root='../../data/',
                                          train=False, 
                                          transform=transforms.ToTensor())

# Data loader
# 数据加载器
train_loader = torch.utils.data.DataLoader(dataset=train_dataset,
                                           batch_size=batch_size, 
                                           shuffle=True)

test_loader = torch.utils.data.DataLoader(dataset=test_dataset,
                                          batch_size=batch_size, 
                                          shuffle=False)

# Convolutional neural network (two convolutional layers)
# 卷积神经网络（两个卷积层）
class ConvNet(nn.Module):
    def __init__(self, num_classes=10):
        super(ConvNet, self).__init__()
        self.layer1 = nn.Sequential(
            nn.Conv2d(1, 16, kernel_size=5, stride=1, padding=2),
            nn.BatchNorm2d(16),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=2, stride=2))
        self.layer2 = nn.Sequential(
            nn.Conv2d(16, 32, kernel_size=5, stride=1, padding=2),
            nn.BatchNorm2d(32),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=2, stride=2))
        self.fc = nn.Linear(7*7*32, num_classes)
        
    def forward(self, x):
        out = self.layer1(x)
        out = self.layer2(out)
        out = out.reshape(out.size(0), -1)
        out = self.fc(out)
        return out

model = ConvNet(num_classes).to(device)

# Loss and optimizer
# 损失和优化
criterion = nn.CrossEntropyLoss()
optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)

# Train the model
# 训练模型
total_step = len(train_loader)
for epoch in range(num_epochs):
    for i, (images, labels) in enumerate(train_loader):
        images = images.to(device)
        labels = labels.to(device)
        
        # Forward pass
        # 正向传播
        outputs = model(images)
        loss = criterion(outputs, labels)
        
        # Backward and optimize
        # 反向传播并优化
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        
        if (i+1) % 100 == 0:
            print ('Epoch [{}/{}], Step [{}/{}], Loss: {:.4f}' 
                   .format(epoch+1, num_epochs, i+1, total_step, loss.item()))

# Test the model
# 测试模型
model.eval()  # eval mode (batchnorm uses moving mean/variance instead of mini-batch mean/variance)
              # eval 模式 （批处理标准使用移动均值/方差而不是小批均值/方差）‎
with torch.no_grad():
    correct = 0
    total = 0
    for images, labels in test_loader:
        images = images.to(device)
        labels = labels.to(device)
        outputs = model(images)
        _, predicted = torch.max(outputs.data, 1)
        total += labels.size(0)
        correct += (predicted == labels).sum().item()

    print('Test Accuracy of the model on the 10000 test images: {} %'.format(100 * correct / total))
    print('测试10000张图像，模型的准确率为： {} %'.format(100 * correct / total))

# Save the model checkpoint
# 保存模型检查点
torch.save(model.state_dict(), 'model.ckpt')
