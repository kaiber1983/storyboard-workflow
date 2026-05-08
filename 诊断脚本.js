// 诊断脚本 - 在浏览器控制台中运行

console.log('=== 开始诊断 ===');

// 1. 检查按钮
const btn1 = document.getElementById('storyboardApiConfig');
const btn2 = document.getElementById('imageApiConfig');
console.log('分镜API配置按钮:', btn1);
console.log('生图API配置按钮:', btn2);

// 2. 检查模态窗口
const modal1 = document.getElementById('storyboardApiModal');
const modal2 = document.getElementById('imageApiModal');
console.log('分镜API模态窗口:', modal1);
console.log('生图API模态窗口:', modal2);

// 3. 检查 CSS 类
if (modal1) {
  console.log('分镜模态窗口类名:', modal1.className);
  console.log('分镜模态窗口样式:', window.getComputedStyle(modal1).display);
}
if (modal2) {
  console.log('生图模态窗口类名:', modal2.className);
  console.log('生图模态窗口样式:', window.getComputedStyle(modal2).display);
}

// 4. 测试手动打开
console.log('=== 尝试手动打开模态窗口 ===');
if (modal1) {
  modal1.classList.add('show');
  console.log('已添加 show 类到分镜模态窗口');
  console.log('当前 display:', window.getComputedStyle(modal1).display);
}

// 5. 检查事件监听器
console.log('=== 检查事件监听器 ===');
if (btn1) {
  console.log('分镜按钮事件监听器数量:', getEventListeners(btn1));
}
if (btn2) {
  console.log('生图按钮事件监听器数量:', getEventListeners(btn2));
}

// 6. 手动绑定测试
console.log('=== 手动绑定测试事件 ===');
if (btn1 && modal1) {
  btn1.onclick = function() {
    console.log('✅ 分镜按钮被点击！');
    modal1.classList.add('show');
    console.log('已添加 show 类');
  };
  console.log('已绑定分镜按钮点击事件');
}

if (btn2 && modal2) {
  btn2.onclick = function() {
    console.log('✅ 生图按钮被点击！');
    modal2.classList.add('show');
    console.log('已添加 show 类');
  };
  console.log('已绑定生图按钮点击事件');
}

console.log('=== 诊断完成 ===');
console.log('现在请点击按钮测试');
