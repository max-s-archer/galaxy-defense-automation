# Galaxy Defense Automation

[English](README.md) | 简体中文

这是一个用 Python 编写的 Galaxy Defense 自动选卡工具。首个验证设备是运行 Android 16 的三星 Galaxy S23 Ultra。
本页是英文 README 的简体中文版。

## 第一阶段

脚本识别两种选卡界面，按卡片位置做选择。

- **三卡选择**：点击最左边的卡片一次，游戏自动回到战斗。
- **五卡抽取**：先翻开左上角的卡片。如果游戏提示再抽一次，就翻开上排中间的卡片。
  抽取完成后，点击游戏中的“獲得”按钮，回到战斗。

战斗中或遇到无法识别的界面时，脚本等待下一次检查。

## 项目状态

第一阶段已完成开发，并通过真机验证。第二阶段的范围待定。

## 截取一张游戏画面

在 macOS 上安装 Python 3.7 或更高版本和 Android SDK Platform-Tools。在手机上启用 USB 调试，通过 USB
连接电脑，解锁手机并允许调试。如果使用 Android Studio 默认的 SDK 安装位置，在当前 zsh 终端中执行：

```sh
export PATH="$HOME/Library/Android/sdk/platform-tools:$PATH"
```

在手机上打开游戏，在仓库根目录执行以下命令。先确认设备列表中手机的状态为 `device`，再截图。

```sh
adb devices -l
python3 scripts/capture_screen.py battle.png
```

用 macOS 的“预览”打开 `battle.png`，确认游戏画面完整、方向正确、文字清晰。切换游戏画面后，
换一个文件名再截一张。每次调用保存一张原始 PNG，已有文件会保留。
要验证连接失败时的行为，可以断开 USB，用新的文件名运行脚本。预期脚本以非零状态码退出，且没有生成截图。

## 离线识别截图

在仓库根目录创建虚拟环境、安装依赖，然后分析一张已保存的竖屏截图。把示例中的 `battle_three_cards.png`
替换成自己的截图路径。识别器依据 S23 Ultra 上观察到的竖屏布局判断状态。

macOS（zsh）：

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python scripts/detect_screen.py battle_three_cards.png
```

Windows（PowerShell）：

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe scripts\detect_screen.py battle_three_cards.png
```

| 终端输出 | 游戏画面 |
| --- | --- |
| `three_cards` | 三张正面朝上的升级卡，等待选择 |
| `five_cards` | 五张背面朝上的卡，等待抽取 |
| `five_cards_draw_again` | 已翻开第一张，游戏提示再抽一次 |
| `five_cards_claim` | 抽取已完成，金色“獲得”按钮可见 |
| `battle_won` | 挑战完成，显示奖励和伤害统计 |
| `battle_lost` | 挑战失败，显示奖励和伤害统计 |
| `wait` | 正在战斗，或当前画面无法识别 |

## 在手机上执行一步

通过 USB 连接手机并打开游戏。在前面创建的 Python 环境中，先预览当前画面对应的动作，再执行一步。
macOS（zsh）命令如下。

```sh
.venv/bin/python scripts/run_step.py --dry-run
.venv/bin/python scripts/run_step.py
```

在 Windows PowerShell 中使用 `.\.venv\Scripts\python.exe scripts\run_step.py`，参数相同。
每次调用都会重新截图。可以在三卡页执行一步，观察最左卡是否被选中、战斗是否恢复。回到战斗后再执行一次，
预期输出 `wait: no tap`。在五卡页，每运行一次执行一个动作，依次完成首抽、按提示追加抽取和领取。

## 战斗中持续轮询

打开游戏后，在 macOS 上运行 `.venv/bin/python scripts/run_step.py --loop`；
在 Windows PowerShell 中运行 `.\.venv\Scripts\python.exe scripts\run_step.py --loop`。按 `Ctrl+C` 停止轮询。

### 轮询选项

| 参数 | 默认值 | 用法 |
| --- | --- | --- |
| `--interval SECONDS` | `2` | 设置每轮检查完成后的等待秒数。`--loop --interval 1` 表示每轮结束后等待 1 秒。 |
| `--dry-run` | 关闭 | `--loop --dry-run` 在终端预览每轮判断和计划点击的位置。 |
| `--stop-on-result` | 关闭 | `--loop --stop-on-result` 在确认一局的胜负后退出脚本。 |

连续两次检查得到相同的胜负结果时，脚本确认本局结束，并为这次结算打印一次 `Result: battle_won` 或
`Result: battle_lost`。默认继续轮询，你可以手动开始下一局。启用 `--stop-on-result` 后，Python 进程正常退出，
手机停留在结算页。预览模式也遵循相同的退出规则。

每一轮识别到三卡页，脚本都会点击一次左卡，因此也能处理连续升级。五卡页则在进入新的选卡状态时执行一次
对应动作。如果之后连续三轮仍检测到同一状态，脚本会提示检查手机并继续观察。连续两轮返回 `wait` 后，
再次出现相同的五卡状态时可以重新触发动作。截图或点击出错时，轮询停止。

## 仓库信息

- [Agent 协作说明](AGENTS.md)
- [Apache License 2.0](LICENSE)
