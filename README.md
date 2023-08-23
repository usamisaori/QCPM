# qcpm

## 调用：

1. 逐步
   
   + `Circuit`: 设置 `optimize=False` 则读入完全不优化的线路(默认为 True)，`system`: "IBM" 或者 "Surface"，**读入的**数据的平台信息
   + `mapper.execute` 时候不设置 `strategy` 默认精确匹配
   + `circuit.save`: 新加 `to` 参数指定输出平台的
```python
from qcpm import Mapper, Circuit

# Step 1. init mapper
mapper = Mapper()

# Step 2. load and int circuit
circuit = Circuit('data.qasm', optimize=True, system='IBM')

# Step 3. execute mapping
mapper.execute(circuit, strategy='MCM')

# Step 4. save results.
circuit.save('data_mapped.qasm', to='Surface')
```

2. `QCPM.execute` 的参数: `from`, `to` 可以是文件也可以是文件夹路径。`strategy` 默认不指定为精确匹配。`system` 可以：1. `system="IBM"` 指定一个平台格式，这时候输入输出都为同一格式，不指定默认为 "IBM"。2. `system=["IBM", "Surface"]`，列表，分别是读入格式与输出格式。
```python
from qcpm import QCPatternMapper
QCPM = QCPatternMapper()
QCPM.execute(circuit_path, './circuit_after', 
    strategy='MCM', system=['IBM', 'Surface'])
# QCPM.execute(circuit_path, './circuit_after', 
#     strategy='MCM', system='IBM')
```

---

## 输入格式：

+ circuit data: (.qasm)
  
  `example.qasm`:
  ```
  OPENQASM 2.0;
  include "qelib1.inc";
  qreg q[16];
  creg c[16];
  cx q[4],q[1];
  t q[4];
  t q[2];
  q[0];
  ...
  ```
 
 + pattern data: (.json)
    
    `pattern.json`:
    ```json
    [
        {
            "src": [
                ["cx", [0, 1]],
                ["cx", [1, 2]],
                ["cx", [0, 1]]
            ],
            "dst": [
                ["cx", [0, 2]],
                ["cx", [1, 2]]
            ]
        },
        ...
    ]
    ```
    上述 pattern 描述了如下映射：
    ```
    |0>: - o ----- o -
           |       |
    |1>: - X - o - X -
               |
    |2>: ----- X -----
    ```
    到
    ```
    |0>: - o -----
           |       
    |1>: - | - o -
           |   |
    |2>: - X - X -
    ```
 + 用于 Reduction/Commutation 的模式也按相同的语法描述。例如 `commutation.json`:
    ```json
    [
    {
        "src": [
            ["h", [0]],
            ["s", [0]],
            ["h", [0]]
        ],
        "dst": [
            ["sdg", [0]],
            ["h", [0]],
            ["sdg", [0]]
        ]
    },
    ...
    ```
    相关文件在 `qcpm/optimization/rules` 下

---

 ## 运行

1. 逐步手动运行
   + `Mapper` 从 json 文件表示的映射关系中构建映射模式，用于内部的映射处理。

   + `Circuit` 从 qasm 中读入数据并构建对象。

   + `mapper.execute(circuit)`: 在线路 circuit 上应用映射 mapper

   + `circuit.save(circuit_output_path)`: 将处理后的 Circuit 对象以 qasm 数据的格式输出至指定文件。

   ```python
   from qcpm import Mapper, Circuit

   mapper = Mapper(pattern_path) # ./.json
   circuit = Circuit(circuit_path) # ./.qasm

   mapper.execute(circuit)

   circuit.save(circuit_output) # ./.qasm
   ```
2. 使用封装的 `QCPatternMapper` 运行
    
    其中 `log=` 参数给定日志文件的输出路径。不设置的情况下默认为标准输出。

    `execute` 函数的参数分别为输入的 qasm 文件路径与输出的 qasm 路径(处理后)。不设置的情况下则不保存映射后的结果。
    ```python
    from qcpm import QCPatternMapper

    QCPM = QCPatternMapper(pattern_path, log=log_path)
    QCPM.execute(circuit_path, circuit_output)
    ```
---

## 输出

测试结果的输出见 `log.txt`

包括：

根据输入构建的映射模式：

```
Pattern  1
cx [0, 1]
cx [1, 2]
cx [0, 1]
 => 
cx [0, 2]
cx [1, 2]
...
```

线路根据对应模式查找的可替换的候选项：

```
Pattern:  1

pos:  73 # 匹配处的第一个门操作在序列中的位置
# 以下是匹配到的对应的门操作序列
No: 73, cx [4, 1]
No: 74, cx [1, 2]
No: 75, cx [4, 1]
...
# 所有候选项的匹配位置
Candidate: 
 [73, 75]
```
候选替换方案生成：
1. 按节约(saving)成本的排序输出所有可能的备选替换方案(排除冲突)(old)：

    ```
    Rank: 1
    Plan: 1
    [Pos: 54 xx => I,
    Pos: 76 cc => c,
    Pos: 78 cc => c,
    Pos: 130 cc => I,
    Pos: 133 cc => I,
    Pos: 194 cc => c,
    Pos: 230 xcx => c]
    Change: 7, Saving: 18

    Rank: 2
    Plan: 2
    [Pos: 54 xx => I,
    Pos: 76 cc => c,
    Pos: 78 cc => c,
    Pos: 130 cc => I,
    Pos: 133 cc => I,
    Pos: 195 cc => c,
    Pos: 230 xcx => c]
    Change: 7, Saving: 18

    ......

    Total Plans: 36
    ```

    其中 `Change` 为该方案需实际替换的模式数量(非替换的门数量)， `Saving` 为该方案所能节省的成本(用门的深度来衡量)

2. 使用蒙特卡洛模拟的情况下的候选方案输出日志如下(当前实现)：

    ```
    **********************
    *                    *
    *   Generate Plans   *
    *                    *
    **********************

    Sorted Candidates: 

    [Pos: [1, 4] cc => c, Pos: [1, 4, 5] ccc => cc, Pos: [4, 5] cc => c, Pos: [5, 6] cc => c, Pos: [5, 8] cc => I, Pos: [5, 6, 8] ccc => cc, Pos: [6, 7] cc => c, Pos: [7, 9] cc => c, Pos: [7, 10] cc => I, Pos: [7, 9, 10] ccc => cc, Pos: [15, 16] cc => c, Pos: [16, 17] cc => c, Pos: [22, 25] xx => I, Pos: [33, 37] xx => I, Pos: [35, 36] cc => c, Pos: [40, 42] xx => I, Pos: [41, 43] cc => I, Pos: [43, 44] cc => c]

    Monte Carlo-based plan searching

    ------------

    Expansion: Candidates size: 3

    Pos: [1, 4] cc => c
    Pos: [1, 4, 5] ccc => cc
    Pos: [4, 5] cc => c

    Selected: Pos: [1, 4] cc => c
        ... xchxccccccccxxcccchc ... 
    target:  ^  ^               

    ----------

    Expansion: Candidates size: 4

    Pos: [5, 6] cc => c
    Pos: [5, 8] cc => I
    Pos: [5, 6, 8] ccc => cc
    Pos: [6, 7] cc => c

    Selected: Pos: [5, 8] cc => I
        ... cccccccxxcccchcRhxcc ... 
    target: ^  ^                

    ......

    Complete Plan: 

    Pos: [1, 4] cc => c
    Pos: [5, 8] cc => I
    Pos: [7, 10] cc => I
    Pos: [16, 17] cc => c
    Pos: [22, 25] xx => I
    Pos: [33, 37] xx => I
    Pos: [35, 36] cc => c
    Pos: [40, 42] xx => I
    Pos: [41, 43] cc => I

    Total Saving: 24
    ```

根据选择的最优方案进行映射：

```
**************************
*                        *
*   Apply Mapping Plan   *
*                        *
**************************

Selected Best Plan: 
[Pos: [1, 4] cc => c,
 Pos: [5, 8] cc => I,
 Pos: [7, 10] cc => I,
 Pos: [16, 17] cc => c,
 Pos: [22, 25] xx => I,
 Pos: [33, 37] xx => I,
 Pos: [35, 36] cc => c,
 Pos: [40, 42] xx => I,
 Pos: [41, 43] cc => I]
Change: 9, Saving: 24

Circuit before: xchxccccccccxxcccchcRhxccxcchRhchxcccxchxcxccch
---------------
Apply:  Pos: [1, 4] cc => c
Apply:  Pos: [5, 8] cc => I
Apply:  Pos: [7, 10] cc => I
Apply:  Pos: [16, 17] cc => c
Apply:  Pos: [22, 25] xx => I
Apply:  Pos: [33, 37] xx => I
Apply:  Pos: [35, 36] cc => c
Apply:  Pos: [40, 42] xx => I
Apply:  Pos: [41, 43] cc => I
---------------
Circuit after: xchxcccxxccchcRhcccchRhchccchcch

```