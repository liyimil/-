#!/bin/bash
# check-submission.sh — Day1 提交包完整性检查脚本
#
# 用法: bash check-submission.sh [目录路径]
#   - 指向 day1-submission/（含 rag-assistant/ 和 bug-fix-lab/ 子目录）
#   - 或直接指向 rag-assistant/ 目录（自动检测）
# 默认检查当前目录

TARGET="${1:-.}"
PASS=0
WARN=0
BLOCKED=0

# 自动检测目录类型
if [ -f "$TARGET/src/main.py" ]; then
  # TARGET 本身就是 rag-assistant 目录
  RAG_DIR="${TARGET%/}"
  # 尝试在 rag-assistant 同级的 bug-fix-lab
  BUG_PARENT="$(dirname "${TARGET%/}")"
  BUG_DIR="${BUG_PARENT}/bug-fix-lab"
elif [ -f "$TARGET/rag-assistant/src/main.py" ]; then
  # TARGET 是 day1-submission/ 目录
  RAG_DIR="${TARGET%/}/rag-assistant"
  BUG_DIR="${TARGET%/}/bug-fix-lab"
else
  # 默认假设 day1-submission/ 结构
  RAG_DIR="${TARGET%/}/rag-assistant"
  BUG_DIR="${TARGET%/}/bug-fix-lab"
fi

echo "========================================"
echo " Day1 提交包完整性检查"
echo " 目标: $TARGET"
echo " RAG:  $RAG_DIR"
echo " Bug:  $BUG_DIR"
echo "========================================"
echo ""

# ==========================================
# 辅助函数 — 使用直接路径
# ==========================================

check_file() {
  local fpath="$1"
  local label="$2"
  if [ -f "$fpath" ]; then
    echo "  ✅ $label: $fpath"
    PASS=$((PASS + 1))
    return 0
  else
    echo "  ❌ $label: $fpath (缺失)"
    BLOCKED=$((BLOCKED + 1))
    return 1
  fi
}

check_dir() {
  local dpath="$1"
  local label="$2"
  if [ -d "$dpath" ]; then
    echo "  ✅ $label: $dpath/"
    PASS=$((PASS + 1))
    return 0
  else
    echo "  ⚠️  $label: $dpath/ (不存在)"
    WARN=$((WARN + 1))
    return 1
  fi
}

# ==========================================
# 1. 目录结构检查
# ==========================================
echo "--- 1. 目录结构 ---"

check_dir "$RAG_DIR" "RAG项目目录"
check_dir "$RAG_DIR/src" "  src/"
check_dir "$RAG_DIR/data" "  data/"
check_dir "$RAG_DIR/docs" "  docs/"
check_dir "$RAG_DIR/tests" "  tests/"
check_dir "$BUG_DIR" "Bug修复目录"

echo ""

# ==========================================
# 2. 6 类标准文件检查
# ==========================================
echo "--- 2. 标准文件 ---"

check_file "$RAG_DIR/docs/spec.md" "spec.md"
check_file "$RAG_DIR/docs/design.md" "design.md"
check_file "$RAG_DIR/docs/test-record.md" "test-record.md"
check_file "$RAG_DIR/README.md" "README.md"

# ai-log.md 可能在多处
AI_LOG_PATH=""
for loc in "$TARGET/ai-log.md" "$RAG_DIR/docs/ai-log.md" "$RAG_DIR/ai-log.md"; do
  [ -f "$loc" ] && AI_LOG_PATH="$loc" && break
done
if [ -n "$AI_LOG_PATH" ]; then
  echo "  ✅ ai-log.md: $AI_LOG_PATH"
  PASS=$((PASS + 1))
else
  echo "  ❌ ai-log.md (缺失)"
  BLOCKED=$((BLOCKED + 1))
fi

# reflection.md 可能在多处
REFL_PATH=""
for loc in "$TARGET/reflection.md" "$RAG_DIR/docs/reflection.md"; do
  [ -f "$loc" ] && REFL_PATH="$loc" && break
done
if [ -n "$REFL_PATH" ]; then
  echo "  ✅ reflection.md: $REFL_PATH"
  PASS=$((PASS + 1))
else
  echo "  ⚠️  reflection.md (缺失)"
  WARN=$((WARN + 1))
fi

echo ""

# ==========================================
# 3. ai-log 质量检查
# ==========================================
echo "--- 3. ai-log 质量 ---"

if [ -n "$AI_LOG_PATH" ]; then
  HAS_FIELDS=0
  grep -q "目的" "$AI_LOG_PATH" 2>/dev/null && HAS_FIELDS=$((HAS_FIELDS + 1))
  grep -q "输入" "$AI_LOG_PATH" 2>/dev/null && HAS_FIELDS=$((HAS_FIELDS + 1))
  grep -q "建议" "$AI_LOG_PATH" 2>/dev/null && HAS_FIELDS=$((HAS_FIELDS + 1))
  grep -q "人工判断" "$AI_LOG_PATH" 2>/dev/null && HAS_FIELDS=$((HAS_FIELDS + 1))
  grep -q "验证" "$AI_LOG_PATH" 2>/dev/null && HAS_FIELDS=$((HAS_FIELDS + 1))

  if [ "$HAS_FIELDS" -ge 4 ]; then
    echo "  ✅ 五字段格式完整 ($HAS_FIELDS/5)"
    PASS=$((PASS + 1))
  else
    echo "  ⚠️  五字段不完整 ($HAS_FIELDS/5)"
    WARN=$((WARN + 1))
  fi

  if ! grep -A2 "人工判断" "$AI_LOG_PATH" | grep -qiE "(AI说得对|AI说的都对|^同意$|^无$|^没问题$)"; then
    echo "  ✅ 人工判断有实质内容"
    PASS=$((PASS + 1))
  else
    echo "  ⚠️  人工判断可能缺少实质内容"
    WARN=$((WARN + 1))
  fi

  ENTRY_COUNT=$(grep -c "^## 第" "$AI_LOG_PATH" 2>/dev/null || echo 0)
  if [ "$ENTRY_COUNT" -ge 7 ]; then
    echo "  ✅ ai-log 条目数: $ENTRY_COUNT (≥7)"
    PASS=$((PASS + 1))
  elif [ "$ENTRY_COUNT" -gt 0 ]; then
    echo "  ⚠️  ai-log 条目数: $ENTRY_COUNT (不足7条)"
    WARN=$((WARN + 1))
  else
    echo "  ⚠️  无法统计 ai-log 条目数"
    WARN=$((WARN + 1))
  fi
fi

echo ""

# ==========================================
# 4. README 可复现性检查
# ==========================================
echo "--- 4. README 可复现性 ---"

README_PATH="$RAG_DIR/README.md"
if [ -f "$README_PATH" ]; then
  HAS_INSTALL=0; HAS_RUN=0; HAS_TEST=0
  grep -qiE "(pip install|安装|install)" "$README_PATH" 2>/dev/null && HAS_INSTALL=1
  grep -qiE "(python3 |运行|run)" "$README_PATH" 2>/dev/null && HAS_RUN=1
  grep -qiE "(test|测试)" "$README_PATH" 2>/dev/null && HAS_TEST=1

  if [ "$HAS_INSTALL" -eq 1 ] && [ "$HAS_RUN" -eq 1 ] && [ "$HAS_TEST" -eq 1 ]; then
    echo "  ✅ README 包含安装/运行/测试命令"
    PASS=$((PASS + 1))
  else
    echo "  ⚠️  README 缺少:"
    [ "$HAS_INSTALL" -eq 0 ] && echo "     - 安装命令"
    [ "$HAS_RUN" -eq 0 ] && echo "     - 运行命令"
    [ "$HAS_TEST" -eq 0 ] && echo "     - 测试命令"
    WARN=$((WARN + 1))
  fi
else
  echo "  ❌ 未找到 README.md"
  BLOCKED=$((BLOCKED + 1))
fi

echo ""

# ==========================================
# 5. bug-fix-lab 检查
# ==========================================
echo "--- 5. Bug修复产物 ---"

check_file "$BUG_DIR/reproduction.md" "reproduction.md"
check_file "$BUG_DIR/root-cause.md" "root-cause.md"
check_file "$BUG_DIR/fix-record.md" "fix-record.md"

echo ""

# ==========================================
# 6. RAG 核心文件检查
# ==========================================
echo "--- 6. RAG 核心代码 ---"

check_file "$RAG_DIR/src/main.py" "main.py"
check_file "$RAG_DIR/src/retrieve.py" "retrieve.py"
check_file "$RAG_DIR/src/answer.py" "answer.py"
check_file "$RAG_DIR/data/course-faq.md" "course-faq.md"

RETRIEVE_PATH="$RAG_DIR/src/retrieve.py"
if [ -f "$RETRIEVE_PATH" ] && grep -q "def retrieve" "$RETRIEVE_PATH" 2>/dev/null; then
  LINES=$(grep -v -E '^\s*(//|$)' "$RETRIEVE_PATH" | wc -l)
  if [ "$LINES" -gt 5 ]; then
    echo "  ✅ retrieve.py 有实现内容 ($LINES 行)"
    PASS=$((PASS + 1))
  else
    echo "  ⚠️  retrieve.py 可能仍为空签名版本 ($LINES 行)"
    WARN=$((WARN + 1))
  fi
fi

ANSWER_PATH="$RAG_DIR/src/answer.py"
if [ -f "$ANSWER_PATH" ] && grep -q "def answer" "$ANSWER_PATH" 2>/dev/null; then
  LINES=$(grep -v -E '^\s*(//|$)' "$ANSWER_PATH" | wc -l)
  if [ "$LINES" -gt 5 ]; then
    echo "  ✅ answer.py 有实现内容 ($LINES 行)"
    PASS=$((PASS + 1))
  else
    echo "  ⚠️  answer.py 可能仍为空签名版本 ($LINES 行)"
    WARN=$((WARN + 1))
  fi
fi

echo ""

# ==========================================
# 7. reflection 质量
# ==========================================
echo "--- 7. reflection 质量 ---"

if [ -n "$REFL_PATH" ]; then
  if grep -qiE "(收获很多|学到了很多|都挺难的|加油|下次努力)" "$REFL_PATH"; then
    echo "  ⚠️  reflection 可能包含空洞表述"
    WARN=$((WARN + 1))
  else
    echo "  ✅ reflection 未检测到空洞表述"
    PASS=$((PASS + 1))
  fi

  REFL_LINES=$(wc -l < "$REFL_PATH")
  if [ "$REFL_LINES" -gt 10 ]; then
    echo "  ✅ reflection 内容长度: $REFL_LINES 行 (≥10)"
    PASS=$((PASS + 1))
  else
    echo "  ⚠️  reflection 内容过短 ($REFL_LINES 行)"
    WARN=$((WARN + 1))
  fi
fi

echo ""

# ==========================================
# 总评
# ==========================================
echo "========================================"
echo " 检查结果汇总"
echo "========================================"
echo "  ✅ PASS:    $PASS"
echo "  ⚠️  WARNING: $WARN"
echo "  ❌ BLOCKED: $BLOCKED"
echo "----------------------------------------"

if [ "$BLOCKED" -gt 0 ]; then
  echo " 评级: BLOCKED"
  echo " 原因: 有 $BLOCKED 项关键文件缺失。"
elif [ "$WARN" -gt 2 ]; then
  echo " 评级: WARNING"
  echo " 原因: 有 $WARN 项需要改进。"
else
  echo " 评级: PASS"
  echo " 提交包完整，关键证据文件齐全。"
fi
echo "========================================"

[ "$BLOCKED" -gt 0 ] && exit 2
[ "$WARN" -gt 2 ] && exit 1
exit 0
