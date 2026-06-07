import re

content = open('index.html', 'r', encoding='utf-8').read()
scripts = re.findall(r'<script[^>]*>(.*?)</script>', content, re.DOTALL)
main_js = scripts[7]

checks = [
    ('No corruption fragment', 'active:scale-95 trans         const Footer' not in main_js),
    ('Dismiss button correct', "transition-all'" in main_js or 'transition-all"' in main_js),
    ('MobileHome declared once', main_js.count('const MobileHome') == 1),
    ('Footer declared once', main_js.count('const Footer') == 1),
    ('Home component once', main_js.count('const Home =') == 1),
    ('AboutPage present', 'const AboutPage' in main_js),
    ('CoursesPage present', 'const CoursesPage' in main_js),
    ('GalleryPage present', 'const GalleryPage' in main_js),
    ('EventsPage present', 'const EventsPage' in main_js),
    ('CareersPage present', 'const CareersPage' in main_js),
    ('Paren balance', main_js.count('(') == main_js.count(')')),
    ('Brace balance', main_js.count('{') == main_js.count('}')),
    ('Bracket balance', main_js.count('[') == main_js.count(']')),
]

print('=== PORTAL VALIDATION ===')
all_ok = True
for name, result in checks:
    status = 'PASS' if result else 'FAIL'
    if not result:
        all_ok = False
    print('  [%s] %s' % (status, name))

print()
print('File size: %s bytes' % len(content))
print('OVERALL: %s' % ('ALL GOOD!' if all_ok else 'ISSUES FOUND - CHECK FAILURES ABOVE'))
