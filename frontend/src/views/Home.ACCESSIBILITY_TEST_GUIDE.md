# Home Dashboard Accessibility Testing Guide

## Quick Testing Checklist

### Keyboard Navigation Test (5 minutes)

1. **Open the dashboard** and press `Tab` repeatedly
   - ✓ Skip-to-content link should appear first
   - ✓ Focus moves to refresh button
   - ✓ Focus moves to user profile card
   - ✓ All interactive elements receive visible focus

2. **Test keyboard activation**
   - Press `Enter` on user profile card → Should navigate to profile
   - Press `Space` on user profile card → Should navigate to profile
   - Press `Enter` on refresh button → Should refresh data

3. **Test skip-to-content**
   - Press `Tab` once from page load
   - Press `Enter` on skip link → Should jump to main content

### Screen Reader Test (10 minutes)

#### Windows (NVDA/JAWS):
1. Start NVDA (Insert + N) or JAWS
2. Navigate to dashboard
3. Listen for announcements:
   - "仪表盘" heading
   - "用户资料卡片，点击查看详细信息"
   - Widget titles and descriptions
   - Chart data alternatives

#### macOS (VoiceOver):
1. Enable VoiceOver (Cmd + F5)
2. Navigate with VO + Right Arrow
3. Verify all content is announced

### Visual Focus Test (2 minutes)

1. **Tab through all elements**
   - Blue outline (3px) should appear around focused elements
   - Outline should have 3px offset from element
   - Focus should be clearly visible on all backgrounds

2. **Check focus on different elements**
   - Widgets: Blue outline with shadow
   - Buttons: Blue outline
   - Links: Blue outline
   - Cards: Blue outline with shadow

### Color Contrast Test (3 minutes)

1. **Use browser DevTools**
   - Right-click any text → Inspect
   - Check contrast ratio in Styles panel
   - All text should show ✓ for WCAG AA

2. **Use online tool**
   - Visit: https://webaim.org/resources/contrastchecker/
   - Test primary colors:
     - #111827 on #FFFFFF (gray-900 on white)
     - #2563EB on #FFFFFF (blue-600 on white)
     - #EF4444 on #FFFFFF (red-500 on white)

### Chart Accessibility Test (5 minutes)

1. **With screen reader enabled**
   - Navigate to Steps Statistics Widget
   - Listen for: "环形图显示数据分布：已完成X个，占X%..."
   - Navigate to Trend Analysis Widget
   - Listen for: "面积图显示定时元件、用例元件..."

2. **Check data tables**
   - Screen reader should announce table structure
   - Each data point should be readable

### Loading & Error States Test (3 minutes)

1. **Test loading state**
   - Refresh dashboard
   - Screen reader should announce: "正在加载仪表板数据，请稍候"
   - Visual skeleton should appear

2. **Test error state**
   - Simulate network error (DevTools → Network → Offline)
   - Refresh page
   - Screen reader should announce error immediately
   - Retry button should be keyboard accessible

### Reduced Motion Test (2 minutes)

1. **Enable reduced motion**
   - Windows: Settings → Ease of Access → Display → Show animations
   - macOS: System Preferences → Accessibility → Display → Reduce motion

2. **Verify animations are disabled**
   - Hover effects should not animate
   - Loading spinners should not spin
   - Transitions should be instant

### High Contrast Mode Test (2 minutes)

1. **Enable high contrast**
   - Windows: Alt + Left Shift + Print Screen
   - macOS: System Preferences → Accessibility → Display → Increase contrast

2. **Verify focus indicators**
   - Focus outlines should be thicker (4px)
   - All content should remain visible

## Automated Testing

### Using axe DevTools

```bash
# Install axe DevTools browser extension
# Chrome: https://chrome.google.com/webstore/detail/axe-devtools/lhdoppojpmngadmnindnejefpokejbdd
# Firefox: https://addons.mozilla.org/en-US/firefox/addon/axe-devtools/

# Steps:
1. Open dashboard
2. Open DevTools (F12)
3. Click "axe DevTools" tab
4. Click "Scan ALL of my page"
5. Review results (should be 0 violations)
```

### Using Lighthouse

```bash
# In Chrome DevTools:
1. Open DevTools (F12)
2. Click "Lighthouse" tab
3. Select "Accessibility" category
4. Click "Analyze page load"
5. Review score (should be 95+)
```

### Using WAVE

```bash
# Install WAVE browser extension
# Chrome: https://chrome.google.com/webstore/detail/wave-evaluation-tool/jbbplnpkjmmeebjpijfedlgcdilocofh

# Steps:
1. Open dashboard
2. Click WAVE extension icon
3. Review results
4. Check for errors (should be 0)
```

## Common Issues to Check

### ❌ Potential Problems:
- [ ] Focus not visible on dark backgrounds
- [ ] Screen reader announces decorative images
- [ ] Keyboard trap in modal/dropdown
- [ ] Missing alt text on images
- [ ] Insufficient color contrast
- [ ] No skip-to-content link
- [ ] Charts not accessible to screen readers

### ✅ Expected Behavior:
- [x] All interactive elements keyboard accessible
- [x] Focus indicators clearly visible
- [x] Screen reader announces all content
- [x] Charts have text alternatives
- [x] Color contrast meets WCAG AA
- [x] Skip-to-content link present
- [x] Loading/error states announced

## Test Results Template

```markdown
## Accessibility Test Results

**Date**: YYYY-MM-DD
**Tester**: [Name]
**Browser**: [Chrome/Firefox/Safari/Edge]
**Screen Reader**: [NVDA/JAWS/VoiceOver/Narrator]

### Keyboard Navigation
- [ ] All elements focusable
- [ ] Focus order logical
- [ ] Skip-to-content works
- [ ] No keyboard traps

### Screen Reader
- [ ] All content announced
- [ ] Charts have alternatives
- [ ] Loading states announced
- [ ] Error states announced

### Visual
- [ ] Focus indicators visible
- [ ] Color contrast sufficient
- [ ] Text readable at 200% zoom
- [ ] Works in high contrast mode

### Automated Tools
- [ ] axe DevTools: 0 violations
- [ ] Lighthouse: 95+ score
- [ ] WAVE: 0 errors

### Issues Found
1. [Issue description]
2. [Issue description]

### Notes
[Any additional observations]
```

## Quick Reference: Keyboard Shortcuts

### Navigation:
- `Tab` - Move to next element
- `Shift + Tab` - Move to previous element
- `Enter` - Activate button/link
- `Space` - Activate button/checkbox

### Screen Reader (NVDA):
- `Insert + Down Arrow` - Read next item
- `Insert + Up Arrow` - Read previous item
- `Insert + Space` - Read current item
- `H` - Next heading
- `K` - Next link
- `B` - Next button

### Screen Reader (VoiceOver):
- `VO + Right Arrow` - Next item
- `VO + Left Arrow` - Previous item
- `VO + Space` - Activate item
- `VO + Command + H` - Next heading

## Success Criteria

The dashboard passes accessibility testing if:

1. ✅ All automated tools report 0 critical issues
2. ✅ All interactive elements are keyboard accessible
3. ✅ Screen reader announces all content correctly
4. ✅ Focus indicators are clearly visible
5. ✅ Color contrast meets WCAG AA (4.5:1 minimum)
6. ✅ Charts have accessible alternatives
7. ✅ Loading and error states are announced
8. ✅ Works with reduced motion preferences
9. ✅ Works in high contrast mode
10. ✅ No keyboard traps or navigation issues

## Resources

- [NVDA Download](https://www.nvaccess.org/download/)
- [JAWS Trial](https://www.freedomscientific.com/downloads/jaws)
- [axe DevTools](https://www.deque.com/axe/devtools/)
- [WAVE Extension](https://wave.webaim.org/extension/)
- [WebAIM Contrast Checker](https://webaim.org/resources/contrastchecker/)
