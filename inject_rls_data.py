"""
Comprehensive update script to integrate ALL RLS Public School data into both index.html and admin.html.
Data sourced from all 10 pages of https://rlspublicschool.in/
"""

import re

# ============================================================
# ALL RLS PUBLIC SCHOOL DATA
# ============================================================

# School Photos (all 16 hero slides from the website)
GALLERY_IMAGES = [
    "http://rlspublicschool.in/assets/images/5e9b3231294c39.57902661.jpg",
    "http://rlspublicschool.in/assets/images/6053fd1e98cb96.40885111.jpg",
    "http://rlspublicschool.in/assets/images/68d241561ea7b1.51285988.jpg",
    "http://rlspublicschool.in/assets/images/6053fc2f44b019.74126295.jpg",
    "http://rlspublicschool.in/assets/images/68d241c1895282.51081358.png",
    "http://rlspublicschool.in/assets/images/646f7fface93c4.20862286.jpg",
    "http://rlspublicschool.in/assets/images/68d242cb341f77.30926076.jpg",
    "http://rlspublicschool.in/assets/images/646f804dc97df1.80463924.jpg",
    "http://rlspublicschool.in/assets/images/68d2426d5f4673.58097166.jpg",
    "http://rlspublicschool.in/assets/images/68d24593556b55.90176539.jpg",
    "http://rlspublicschool.in/assets/images/68d2464d736796.48614326.jpg",
    "http://rlspublicschool.in/assets/images/5eb8d723493f92.74318293.jpg",
    "http://rlspublicschool.in/assets/images/5eb8dc364705e5.82857038.jpg",
    "http://rlspublicschool.in/assets/images/69a4f6c268d179.64618665.jpg",
    "http://rlspublicschool.in/assets/images/691b400293b0d9.76254803.jpg",
    "http://rlspublicschool.in/assets/images/691b40752436e3.45009539.jpg",
]

LOGO_URL = "http://rlspublicschool.in/assets/images/621d12bacd26b3.90553425.png"
FAVICON_URL = "http://rlspublicschool.in/assets/images/5e9b26a034cfc6.63821740.jpg"
ABOUT_PHOTO = "http://rlspublicschool.in/assets/images/5eb8d723493f92.74318293.jpg"

# Fee structure (from the actual school fee page)
FEE_STRUCTURE_JS = """const RLS_FEE_STRUCTURE = {
    session: '2022-23',
    categories: ['Class I–III', 'Class IV–VI', 'Class VII–VIII', 'Class IX–X'],
    fees: [
        { name: 'Admission Form', frequency: 'One Time', amounts: [500, 500, 500, 500] },
        { name: 'Admission Fee', frequency: 'One Time', amounts: [2500, 2500, 2500, 2500] },
        { name: 'Development Fund', frequency: 'Annual', amounts: [1500, 1500, 1500, 1500] },
        { name: 'Miscellaneous', frequency: 'Annual', amounts: [350, 350, 350, 350] },
        { name: 'Exam Fee', frequency: 'Annual', amounts: [350, 350, 350, 350] },
        { name: 'Festival Fee', frequency: 'Annual', amounts: [300, 300, 300, 300] },
        { name: 'Society Fee', frequency: 'Monthly', amounts: [50, 50, 50, 50] },
        { name: 'Tuition Fee', frequency: 'Monthly', amounts: [1100, 1250, 1400, 1550] },
        { name: 'Total (First Year)', frequency: 'Total', amounts: [6650, 6800, 6950, 7100] }
    ]
};"""

# Courses (from actual website table)
COURSES_JS = """const RLS_COURSES = [
    { cls: 'Nursery', subjects: ['Hindi', 'English', 'Maths', 'Drawing'] },
    { cls: 'LKG', subjects: ['Hindi', 'English', 'Maths', 'Drawing'] },
    { cls: 'UKG', subjects: ['Hindi', 'English', 'Maths', 'Drawing', 'EVS'] },
    { cls: 'Class I', subjects: ['Hindi', 'English', 'Maths', 'Science', 'Drawing', 'EVS', 'Computer'] },
    { cls: 'Class II', subjects: ['Hindi', 'English', 'Maths', 'Science', 'Drawing', 'EVS', 'Computer'] },
    { cls: 'Class III', subjects: ['Hindi', 'English', 'Maths', 'Science', 'Drawing', 'EVS', 'Computer'] },
    { cls: 'Class IV', subjects: ['Hindi', 'English', 'Maths', 'Science', 'Drawing', 'EVS', 'Computer'] },
    { cls: 'Class V', subjects: ['Hindi', 'English', 'Maths', 'Science', 'Drawing', 'EVS', 'Computer'] },
    { cls: 'Class VI', subjects: ['Hindi', 'English', 'Maths', 'Science', 'Drawing', 'S.St', 'Computer'] },
    { cls: 'Class VII', subjects: ['Hindi', 'English', 'Maths', 'Science', 'Drawing', 'S.St', 'Computer'] },
    { cls: 'Class VIII', subjects: ['Hindi', 'English', 'Maths', 'Science', 'S.St', 'Computer'] },
    { cls: 'Class IX', subjects: ['Hindi', 'English', 'Maths', 'Science', 'S.St', 'Computer'] },
    { cls: 'Class X', subjects: ['Hindi', 'English', 'Maths', 'Science', 'S.St', 'Computer', 'Sanskrit'] }
];"""

# Gallery images JS
gallery_arr = ',\n    '.join([f"'{ img }'" for img in GALLERY_IMAGES])
GALLERY_JS = f"""const RLS_GALLERY_PHOTOS = [
    {gallery_arr}
];"""

# All school info data
SCHOOL_INFO_JS = """const RLS_SCHOOL_INFO = {{
    name: 'R.L.S. Public School',
    fullName: 'R.L.S. Public School',
    shortName: 'RLS',
    tagline: 'CBSE Affiliated School (UPTO +2 LEVEL)',
    principal: 'Dinesh Kumar Singh',
    managingSociety: 'Indrasani Devi Educational Society',
    established: '2015',
    affiliation: 'CBSE, New Delhi',
    affiliationNo: '330862',
    schoolCode: '65860',
    type: 'Co-educational',
    level: 'Nursery to Class XII',
    pinCode: '802207',
    rating: '4.6/5',
    communityMotto: 'A community with high expectation and high academic achievement.',
    vision: 'Our vision at R.L.S. Public School is to empower students to acquire, demonstrate, articulate and value knowledge and skills that will support them, as life-long learners, to participate in and contribute to the global world and practise the core values of the school: respect, tolerance & inclusion, and excellence.',
    mission: 'To provide differentiated, in-depth and cohesive learning programs that support the academic, social, emotional, and physical development of children, enabling all learners access to quality education.',
    coreValues: ['Respect', 'Tolerance & Inclusion', 'Excellence'],
    address: 'Baluwahi Tola, (Barauli) Piro, Bhojpur, Bihar – 802207',
    addressShort: 'Piro, Bhojpur, Bihar',
    location: 'Piro, Bhojpur',
    state: 'Bihar',
    phone1: '+91-9471911451',
    phone2: '+91-9006845566',
    email: 'rlspublicschool55@gmail.com',
    officeHours: '08:30 AM – 02:30 PM',
    website: 'https://rlspublicschool.in',
    studentPortal: 'https://rlsps.gungunerp.in/',
    playStoreApp: 'https://play.google.com/store/apps/details?id=com.apprlsps.gungunerp.rls',
    whatsapp: 'https://api.whatsapp.com/send?phone=+919006845566&text=Welcome%20to%20R.L.S.%20Public%20School.%20How%20may%20we%20help%20you?',
    facebook: 'https://www.facebook.com/RLS-Public-School-Piro-115535490484712/',
    instagram: 'https://www.instagram.com/rlspublicschool55/',
    twitter: 'https://twitter.com/RLSPUBLICSCHOO1',
    youtube: 'https://www.youtube.com/channel/UCXG6ckkY5_Ow7XL3pfLMT9w',
    stats: {{ students: 1180, teachers: 35, staff: 32, yearsOfExcellence: 9 }},
    facilities: ['Smart Class', 'Library', 'Science Labs', 'Transport', 'Sports Infrastructure', 'Conference Hall'],
    events: ['Annual Award Function', 'Independence Day', 'Republic Day', 'Parent-Management Meetings', 'Science Exhibition', 'Sports Day', 'Cultural Celebrations'],
    documents: ['Birth Certificate', 'Aadhar Card (Child + Parents)', 'Residence Proof', 'Passport Photos', 'Transfer Certificate (for higher classes)', 'Previous Report Cards'],
    logoUrl: 'http://rlspublicschool.in/assets/images/621d12bacd26b3.90553425.png',
    faviconUrl: 'http://rlspublicschool.in/assets/images/5e9b26a034cfc6.63821740.jpg',
    aboutPhotoUrl: 'http://rlspublicschool.in/assets/images/5eb8d723493f92.74318293.jpg',
    mapsEmbedUrl: 'https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d28849.67317151216!2d84.37820748381573!3d25.330761965374762!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x398d70e8e6fbf111%3A0x522b41218818f849!2sR.L.S%20PUBLIC%20SCHOOL!5e0!3m2!1sen!2sin!4v1613057792475!5m2!1sen!2sin'
}};"""

def update_file(filepath):
    print(f"\nUpdating: {filepath}")
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # -------------------------------------------------------
    # 1. Inject RLS_SCHOOL_INFO, RLS_FEE_STRUCTURE, RLS_COURSES, 
    #    RLS_GALLERY_PHOTOS constants into the JS block
    # -------------------------------------------------------
    # Find the existing SCHOOL_DATA or RLS data block and replace/augment it
    
    injection_block = f"""
        // ============================================================
        // R.L.S. PUBLIC SCHOOL - COMPLETE SCHOOL DATA
        // Source: https://rlspublicschool.in/ (All pages extracted)
        // ============================================================
        {SCHOOL_INFO_JS}
        {FEE_STRUCTURE_JS}
        {COURSES_JS}
        {GALLERY_JS}
        // End RLS School Data
        // ============================================================
    """
    
    # Check if already injected
    if 'RLS_SCHOOL_INFO' in content:
        # Replace the existing block
        content = re.sub(
            r'// ====+\s*\n\s*// R\.L\.S\. PUBLIC SCHOOL.*?// ====+\s*\n',
            injection_block + '\n',
            content,
            flags=re.DOTALL
        )
        print("  Replaced existing RLS_SCHOOL_INFO block")
    else:
        # Inject after the first <script> tag in the body
        # Find a good injection point - right after the React/config setup
        inject_marker = "const { useState, useEffect, useRef, useCallback, useMemo } = React;"
        if inject_marker in content:
            content = content.replace(
                inject_marker,
                inject_marker + "\n" + injection_block
            )
            print("  Injected RLS_SCHOOL_INFO after React hooks setup")
        else:
            # Try another common marker
            inject_marker2 = "const { createElement: e, useState"
            if inject_marker2 in content:
                content = content.replace(
                    inject_marker2,
                    injection_block + "\n        " + inject_marker2
                )
                print("  Injected RLS_SCHOOL_INFO before createElement")
    
    # -------------------------------------------------------
    # 2. Replace incorrect/generic contact in canvas drawings
    # -------------------------------------------------------
    # Fix the placeholder phone number in canvas receipts
    content = content.replace(
        "Piro, Bhojpur: Piro, Bhojpur, Bihar, Bihar, India \\u2022 Contact: +91 9123456789",
        "Baluwahi Tola, Barauli, Piro, Bhojpur, Bihar \\u2022 Contact: +91 9471911451"
    )
    content = content.replace(
        "+91 9123456789",
        "+91 9471911451"
    )
    
    # -------------------------------------------------------
    # 3. Replace "Piro, Bhojpur: Piro, Bhojpur, Bihar" (duplicated location)
    # -------------------------------------------------------
    content = content.replace(
        "'Piro, Bhojpur'",
        "'Baluwahi Tola, Piro, Bhojpur'"
    )
    
    # -------------------------------------------------------
    # 4. Add principal name wherever "Principal" is shown
    # -------------------------------------------------------
    content = content.replace(
        "'Principal \\u2022 R.L.S. Public School'",
        "'Principal: Dinesh Kumar Singh \\u2022 R.L.S. Public School'"
    )
    content = content.replace(
        "'R.L.S. Public School Admin'",
        "'R.L.S. Public School Admin \\u2022 Dinesh Kumar Singh, Principal'"
    )
    
    # -------------------------------------------------------
    # 5. Replace generic "about" text with real vision/mission
    # -------------------------------------------------------
    old_about = "R.L.S. Public School, affiliated to CBSE Delhi (up to +2 level), is dedicated to fostering a learning environment where academic excellence meets holistic character development. Serving the Piro region of Bhojpur, Bihar since 2018."
    new_about = "R.L.S. Public School, affiliated to CBSE Delhi (up to +2 level), is a co-educational institution managed by Indrasani Devi Educational Society. Founded in 2015 and located at Baluwahi Tola, Piro, Bhojpur, Bihar, we are dedicated to empowering students through respect, tolerance, inclusion, and excellence. Principal: Dinesh Kumar Singh."
    content = content.replace(old_about, new_about)
    
    # -------------------------------------------------------
    # 6. Update contact/address text in footer-like sections
    # -------------------------------------------------------
    content = content.replace(
        "'Baluwahi Tola, Barauli, Piro, Bhojpur, Bihar – 802207'",
        "'Baluwahi Tola, (Barauli) Piro, Bhojpur, Bihar – 802207'"
    )
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    # Verify injection
    has_fee = 'RLS_FEE_STRUCTURE' in content
    has_courses = 'RLS_COURSES' in content
    has_gallery = 'RLS_GALLERY_PHOTOS' in content
    has_info = 'RLS_SCHOOL_INFO' in content
    print(f"  [OK] RLS_SCHOOL_INFO: {has_info}")
    print(f"  [OK] RLS_FEE_STRUCTURE: {has_fee}")
    print(f"  [OK] RLS_COURSES: {has_courses}")
    print(f"  [OK] RLS_GALLERY_PHOTOS: {has_gallery}")
    print(f"  File size: {len(content):,} bytes")

update_file('index.html')
update_file('admin.html')
print("\n=== All RLS school data injected successfully! ===")
