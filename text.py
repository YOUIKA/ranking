import matplotlib.font_manager
import matplotlib.pyplot as plt
fonts = matplotlib.font_manager.findSystemFonts()
print([f for f in fonts if 'Symbola' in f])  # 检查 Symbola 是否在列表中
print(plt.rcParams['font.family'])  # 输出当前默认字体