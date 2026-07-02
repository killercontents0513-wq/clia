# -*- coding: utf-8 -*-
# Single-product injector: replaces/inserts ONE product at the TOP of v6_18 P[] with hand-crafted content
import json, re, sys, io, os, argparse
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE = 'C:/Users/Administrator/Desktop/AI/RetailOBS/3P'
V6_18 = f'{BASE}/LG_AI_Content_Hub_v6_18.html'

# Hand-crafted per-product overrides (one entry per product ID)
# Each override provides the fields that should replace auto-generation
OVERRIDES = {
    'WFV1214BST1': {
        'dv': 'HA', 'cat': 'Washer', 'sub': 'Front Load', 'ico': '🧺',
        'nm': 'LG 12kg Front Load Washer VIVACE — AI DD®, Steam+, Black Steel, Tempered Glass Door (WFV1214BST1)',
        'amz_title': 'LG 12kg Front Load Washing Machine VIVACE — AI DD®, Steam+ (99.9% Allergen Removal), TurboWash™, 6 Motion DD, LG ThinQ Wi-Fi, Black Steel, Tempered Glass Door (WFV1214BST1)',
        'bul': [
            'VIVACE SERIES PERFORMANCE — LG\'s next-generation VIVACE 12kg front-load washer delivers refined Black Steel styling, a premium tempered-glass door and 600mm-standard width, 850mm height, 610mm depth chassis that fits any laundry room.',
            'AI DD® WITH 6 MOTION DD — Up to 18% better fabric protection than Normal cycle. AI Direct Drive weighs every load and reads fabric softness to auto-select the optimal wash motion from 6 DD patterns.',
            'STEAM+ WITH 99.9% ALLERGEN REMOVAL — True Steam+ cycle eliminates 99.9% of common household allergens and leaves clothes with up to 30% fewer wrinkles — certified allergen care for bedding, baby laundry and delicates.',
            'TURBOWASH™ + TWINWASH™ MINI READY — TurboWash™ multi-directional spray rinses detergent faster for a deep clean in record time. Compatible with LG TWINWash™ Mini for small separate loads below the main washer.',
            'LG ThinQ® + FULL STAINLESS STEEL DRUM + 10-YEAR MOTOR WARRANTY — Remote start, cycle monitoring, Smart Diagnosis™, voice control via Alexa/Google Assistant. Full stainless-steel drum and Inverter Direct Drive motor with 10-year warranty.'
        ],
        'amz_desc': 'Experience the LG 12kg VIVACE Front Load Washing Machine (WFV1214BST1) — engineered by LG to deliver next-generation performance, intelligent fabric care and smart home connectivity in a premium Black Steel finish.\\n\\n• VIVACE SERIES — 12kg XL capacity in a standard 600 × 850 × 610 mm footprint with tempered-glass door and Touch LED display.\\n• AI DD® + 6 MOTION DD — Up to 18% better fabric protection; AI auto-selects optimal wash motion per load.\\n• STEAM+ — 99.9% allergen removal and 30% fewer wrinkles.\\n• TURBOWASH™ + TWINWASH™ MINI READY — Faster wash times and optional TWINWash Mini dock for separate small loads.\\n• LG ThinQ® + INVERTER DIRECT DRIVE — Smart Wi-Fi control, voice control, Smart Diagnosis™, and whisper-quiet 10-year-warranty motor.\\n\\nFull stainless-steel drum, refined Black Steel exterior, tempered-glass door. Backed by LG Electronics\' official warranty and LG Saudi Arabia after-sales service network.',
        'kw': 'LG WFV1214BST1 12kg Front Load Washing Machine VIVACE AI DD 6 Motion DD Inverter Direct Drive Steam Plus Allergen Removal TurboWash TWINWash Mini LG ThinQ Wi-Fi Smart Diagnosis Alexa Google Assistant Full Stainless Steel Drum Tempered Glass Door Black Steel Saudi Arabia KSA Official LG 2025 Laundry Home Appliance'
    },
    '65QNED93A6A': {
        'dv': 'HE', 'cat': 'TV', 'sub': 'QNED', 'ico': '📺',
        'nm': 'LG 65" QNED evo AI QNED93 (2025) — 4K 144Hz MiniLED Smart TV, alpha 8 AI Gen2, Dolby Vision + Atmos (65QNED93A6A)',
        'amz_title': 'LG 65" QNED evo AI QNED93 (2025) 4K MiniLED Smart TV — alpha 8 AI Processor Gen2, 144Hz VRR, Dolby Vision + Atmos, AI Magic Remote, webOS25 (65QNED93A6A)',
        'bul': [
            '65" 4K QNED evo MINILED WITH PRECISION DIMMING PRO — MiniLED backlight with Precision Dimming Pro and LG\'s Dynamic QNED Color Pro deliver certified 100% Color Volume (DCI-P3) for reference-grade picture performance.',
            'ALPHA 8 AI PROCESSOR GEN2 + AI PICTURE PRO — ~1.7× greater NPU and ~1.4× faster CPU than the prior generation. AI Super Upscaling 4K and Dynamic Tone Mapping Pro analyse every frame to enhance resolution and depth.',
            '4K 144Hz VRR GAMING — 4 × HDMI 2.1 with 4K 120Hz, VRR up to 144Hz, ALLM, AMD FreeSync and QMS for buttery-smooth console and PC gaming, plus judder-free film playback.',
            'DOLBY VISION + DOLBY ATMOS — Cinema-grade Dolby Vision HDR and Dolby Atmos three-dimensional sound via 2.2-channel 40W audio up-mixed to virtual 9.1.2 channels by alpha 8 AI Sound Pro.',
            'webOS25 + AI MAGIC REMOTE MR25 — AI Concierge, AI Voice ID, AI Search, Amazon Alexa built-in and 5 years of updates via webOS Re:New Program (CES 2025 Innovation Honoree). 1445 × 830 × 58.5 mm slim cabinet.'
        ],
        'amz_desc': 'Experience the LG 65" QNED evo AI QNED93 (2025) — a flagship-class 4K MiniLED Smart TV engineered by LG to deliver reference-grade picture, immersive sound and next-generation AI in one exceptional package.\\n\\n• 4K QNED MINILED + PRECISION DIMMING PRO — Certified 100% Color Volume (DCI-P3) with Dynamic QNED Color Pro.\\n• alpha 8 AI PROCESSOR GEN2 — 1.7× greater NPU, 1.4× faster CPU; AI Picture Pro and AI Sound Pro auto-optimise every frame and audio track.\\n• 144Hz GAMING READY — 4× HDMI 2.1, VRR up to 144Hz, ALLM, FreeSync, QMS — purpose-built for PS5, Xbox Series X and high-refresh PC gaming.\\n• DOLBY VISION + DOLBY ATMOS — Cinema-grade HDR and 2.2-channel 40W audio up-mixed to virtual 9.1.2 via AI Sound Pro.\\n• webOS25 + AI MAGIC REMOTE — AI Concierge, Voice ID, Search; 5-year updates via Re:New Program (CES 2025 Innovation Honoree).\\n\\nSlim 58.5 mm profile (1445 × 830 × 58.5 mm), 400 × 300 mm VESA, Wi-Fi 6, Apple AirPlay and Amazon Alexa built-in. Backed by LG Electronics\' official warranty and LG Saudi Arabia after-sales service network.',
        'kw': 'LG 65QNED93A6A 65 inch QNED 4K MiniLED Smart TV 2025 QNED93 QNED evo alpha 8 AI Processor Gen2 Dynamic QNED Color Pro Precision Dimming Pro AI Picture Pro AI Sound Pro Dolby Vision Atmos 144Hz VRR HDMI 2.1 FreeSync ALLM QMS webOS 25 Magic Remote AI Concierge Voice ID Wi-Fi 6 Saudi Arabia KSA Official LG Television Home Entertainment'
    },
    'WTR22HHP': {
        'dv': 'HA', 'cat': 'Washer', 'sub': 'Top Load', 'ico': '🧺',
        'nm': 'LG 22kg Top Load Washer — AI DD®, TurboWash3D™, Steam, 6 Motion DD, TurboDrum™, Platinum Black (WTR22HHP)',
        'amz_title': 'LG 22kg Top Load Washing Machine — AI DD®, TurboWash3D™ (Full Clean in 30 min), Steam Allergy Care, 6 Motion DD, TurboDrum™, LG ThinQ Wi-Fi, Platinum Black (WTR22HHP)',
        'bul': [
            'XL 22KG CAPACITY + AI TO THE CORE — LG\'s AI sensing detects load size and fabric softness then auto-optimises water, motion and time — one-button perfect laundry for large families, workshops and bulk household washing.',
            'TURBOWASH3D™ + WAVEFORCE + JETSPRAY — A powerful yet gentle clean in just 30 minutes. Multi-directional spray combined with WaveForce strong currents and JetSpray detergent circulation for thorough, fast washing.',
            '6 MOTION DIRECT DRIVE — Six specialised wash motions (Agitating, Swing, Scrubbing, Stepping, Filtration, Rolling) driven by Inverter Direct Drive match the right action to each fabric type, all automatically.',
            'STEAM ALLERGY CARE + STAINLESS STEEL TUB — True Steam helps remove stubborn stains and reduces common household allergens and bacteria. Stainless steel tub is hygienic and corrosion-resistant.',
            'LG ThinQ® WI-FI + PREMIUM PLATINUM BLACK + 10-YEAR MOTOR WARRANTY — Remote start, cycle monitoring, voice control with Alexa/Google Assistant, Smart Diagnosis™. Intuitive digital dial, soft-closing lid, wide lint filter; Inverter Direct Drive motor backed by 10-year warranty.'
        ],
        'amz_desc': 'Experience the LG 22kg Top Load Washing Machine (WTR22HHP) — engineered by LG to deliver XL family capacity, AI-powered fabric care and premium Platinum Black design for modern households in Saudi Arabia.\\n\\n• XL 22KG CAPACITY — Takes on large families, bulky bedding and workshop loads with ease.\\n• AI DD® — Automatically detects load and fabric, picks optimal wash cycle, saves time.\\n• TURBOWASH3D™ — Full wash in 30 minutes via WaveForce + JetSpray + multi-directional spray.\\n• 6 MOTION DD — Six specialised motions driven by Inverter Direct Drive for precision fabric care.\\n• STEAM ALLERGY CARE — Reduces allergens, bacteria and stubborn stains.\\n• LG ThinQ® — Wi-Fi remote start, cycle monitoring, voice control and Smart Diagnosis™.\\n\\nStainless steel tub, soft-closing top lid, wide lint filter, intuitive digital dial, premium Platinum Black finish. Backed by LG Electronics\' official warranty and LG Saudi Arabia after-sales service network. 10-year Inverter Direct Drive motor warranty.',
        'kw': 'LG WTR22HHP 22kg Top Load Washing Machine AI DD TurboWash3D Steam Allergy Care 6 Motion DD TurboDrum WaveForce JetSpray Inverter Direct Drive LG ThinQ Wi-Fi Smart Diagnosis Alexa Google Assistant Soft Closing Lid Wide Lint Filter Stainless Steel Tub Platinum Black Saudi Arabia KSA Official LG 2025 Large Capacity Family Laundry Home Appliance'
    },
    'WS2112BST': {
        'dv': 'HA', 'cat': 'Washer-Dryer', 'sub': 'Front Load', 'ico': '🧺',
        'nm': 'LG 21kg Washer + 12kg Dryer Combo — AI DD®, TurboWash3D™, Steam, LG ThinQ Wi-Fi, Stone Silver (WS2112BST)',
        'amz_title': 'LG 21kg Washer + 12kg Dryer Combo Front Load — AI DD®, TurboWash3D™, Steam, 6 Motion DD, Add Item, LG ThinQ Wi-Fi, Stone Silver (WS2112BST)',
        'bul': [
            'XL 21KG WASH + 12KG DRY — COMBO IN ONE — A full-size 21kg front-load washer paired with a built-in 12kg dryer handles the biggest family laundry and bulky bedding in one appliance. No second machine, no shuffling loads around.',
            'AI DD® WITH 14.5% MORE FABRIC PROTECTION — AI Direct Drive senses load weight and fabric softness, then auto-selects the optimal motion from LG\'s 6 Motion DD patterns for superior cleaning and gentler fabric care.',
            'TURBOWASH3D™ + STEAM HYGIENE — TurboWash3D™ multi-directional spray combined with proven DD motion delivers a fast, thorough wash. True Steam reduces common household allergens and bacteria — kinder for sensitive skin.',
            'ADD ITEM, CHILD LOCK, REMOTE START — Safely pause the cycle to drop in a forgotten sock or shirt. Child Lock keeps little hands out. LG ThinQ® remote start, cycle monitoring, Smart Diagnosis™ and voice control (Alexa, Google Assistant).',
            'PREMIUM STONE SILVER DESIGN + 10-YEAR MOTOR WARRANTY — 700 × 990 × 770 mm chassis in sleek Stone Silver with LED display. Inverter Direct Drive motor runs whisper-quiet even on high-speed spin — backed by LG\'s 10-year motor warranty.'
        ],
        'amz_desc': 'Experience the LG 21kg Washer + 12kg Dryer Combo (WS2112BST) — engineered by LG to deliver XL all-in-one laundry performance, intelligent fabric care and smart home connectivity in a premium Stone Silver finish.\\n\\n• XL CAPACITY COMBO — 21kg wash + 12kg dry in one slim 700 × 990 × 770 mm chassis.\\n• AI DD® — 14.5% more fabric protection via AI-selected wash motions from 6 Motion DD patterns.\\n• TURBOWASH3D™ + STEAM — Fast wash with multi-directional spray; Steam for hygiene and allergen reduction.\\n• ADD ITEM + SMART CONVENIENCE — Pause to add a sock mid-cycle; Child Lock; Remote Start via LG ThinQ®.\\n• QUIET INVERTER DIRECT DRIVE — Vibration sensor, low noise, 10-year motor warranty.\\n• LG ThinQ® Wi-Fi + VOICE — Smart Diagnosis™, hands-free Alexa / Google Assistant.\\n\\nStone Silver finish, LED display, full stainless drum. Backed by LG Electronics\' official warranty and LG Saudi Arabia after-sales service network.',
        'kw': 'LG WS2112BST 21kg Washer 12kg Dryer Combo Front Load AI DD 6 Motion DD Inverter Direct Drive TurboWash3D Steam Allergy Care Add Item Child Lock Remote Start LG ThinQ Wi-Fi Smart Diagnosis Alexa Google Assistant LED Display Stone Silver Saudi Arabia KSA Official LG 2025 All in One Family XL Capacity Laundry Home Appliance'
    },
    'WTT1108OW1': {
        'dv': 'HA', 'cat': 'Washer', 'sub': 'Twin Tub', 'ico': '🧺',
        'nm': 'LG 10.5kg Twin Tub Washing Machine — Roller Jet Pulsator, Punch+3, Rat Away, White (WTT1108OW1)',
        'amz_title': 'LG 10.5kg Twin Tub Washing Machine — 10.5kg Wash + 8kg Spin, Roller Jet Pulsator, Punch+3, 3 Programs, Rat Away Technology, Anti-Vibration, White (WTT1108OW1)',
        'bul': [
            'LARGE 10.5KG WASH + 8KG SPIN TWIN-TUB DESIGN — Separate wash and spin tubs let you wash one load while spin-drying another. Ideal for large families, workshop overalls, and bulk laundry days. Cuts total laundry time significantly versus single-tub machines.',
            'ROLLER JET PULSATOR + PUNCH+3 WASH ACTION — LG\'s Roller Jet Pulsator combined with Punch+3 triple-action creates powerful, uniform water currents that thoroughly rub clothes clean while protecting fabric integrity.',
            '3 WASH PROGRAMS + SOAK — Simple mechanical dial with Gentle, Normal and Strong settings plus a dedicated Soak function (up to 20 min) handles everything from delicates and synthetics to heavily soiled workwear. Hot & Cold water feed.',
            'RAT AWAY TECHNOLOGY — LG\'s unique anti-pest bottom design shields internal hoses and wiring from rodent damage — a genuinely practical safeguard for outdoor laundry rooms, villas, and utility spaces common in Saudi Arabia.',
            'STABLE, DURABLE BUILD — Anti-Vibration Rubber Feet keep the washer steady during high-speed spin. Built-in Lint Filter traps fluff and fibres for cleaner rinses. Durable White polypropylene cabinet (905 × 1025 × 545 mm, 32 kg) built for years of heavy household use.'
        ],
        'amz_desc': 'Experience the LG 10.5kg Twin Tub Washing Machine (WTT1108OW1) — a practical, hard-working twin-tub engineered by LG for large families and heavy-duty laundry in Saudi Arabia.\\n\\n• DUAL-TUB PRODUCTIVITY — 10.5kg wash tub + 8kg spin tub let you wash and spin-dry simultaneously.\\n• ROLLER JET PULSATOR + PUNCH+3 — Powerful triple-action water currents clean thoroughly while protecting fabrics.\\n• 3 WASH PROGRAMS + SOAK — Gentle, Normal, Strong settings with 20-min Soak and Hot & Cold water feed cover every fabric type.\\n• RAT AWAY TECHNOLOGY — LG\'s signature anti-pest design shields internal components — ideal for outdoor laundry areas.\\n• DURABLE BUILD — Anti-Vibration Rubber feet, built-in Lint Filter, durable White polypropylene cabinet.\\n\\nTrusted LG engineering, simple mechanical reliability, and high-capacity performance in a compact 905 × 1025 × 545 mm footprint. Backed by LG Electronics\' official warranty and LG Saudi Arabia after-sales service network.',
        'kw': 'LG WTT1108OW1 Twin Tub Washing Machine 10.5kg Roller Jet Pulsator Punch 3 Three Wash Programs Gentle Normal Strong Rat Away Technology Anti Vibration Rubber Lint Filter Soak Hot Cold Water 8kg Spin Tub Dual Tub Manual Washer White Polypropylene Saudi Arabia KSA Family Large Capacity Budget 2025 LG Home Appliance'
    },
    'WFN1510WHT': {
        'dv': 'HA', 'cat': 'Washer', 'sub': 'Front Load', 'ico': '🧺',
        'nm': 'LG 15kg Front Load Washing Machine with AI DD® & Steam — Essence White (WFN1510WHT)',
        'amz_title': 'LG 15kg Front Load Washing Machine with AI DD®, Steam, TurboWash™ 39, Allergy Care, LG ThinQ Wi-Fi — Essence White, 10-Year Inverter Motor Warranty (WFN1510WHT)',
        'bul': [
            'EXTRA-LARGE 15KG CAPACITY — Spacious stainless-steel drum handles a king-size duvet, curtains or a full family wash in a single cycle, while fitting within an LG-standard depth footprint so it integrates seamlessly into tighter laundry rooms.',
            'AI DIRECT DRIVE® (AI DD®) + 6 MOTION DD — Intelligent sensors weigh every load and read fabric softness, then automatically pick from six optimised wash motions to protect clothes and deliver up to 18% better fabric care than standard motion.',
            'TURBOWASH™ 39 + ALLERGY CARE™ WITH STEAM — Multi-directional spray delivers a deep clean in as little as 39 minutes. The BAF-certified Allergy Care™ Steam cycle helps reduce common household allergens in bedding, soft toys and baby laundry.',
            'LG ThinQ® WI-FI + VOICE + SMART DIAGNOSIS™ — Start, monitor and diagnose from anywhere via the LG ThinQ® app. Hands-free with Amazon Alexa and Google Assistant, with instant Smart Diagnosis™ support through your phone.',
            'QUIET INVERTER DIRECT DRIVE + 10-YEAR MOTOR WARRANTY — Belt-less Inverter Direct Drive motor with vibration sensor runs whisper-quiet and is built to last, backed by LG\'s 10-year motor warranty. Premium Essence White (Glossy) finish with black-tinted tempered-glass door.'
        ],
        'amz_desc': 'Experience the LG 15kg Front Load Washing Machine (WFN1510WHT) — engineered by LG to deliver XL-capacity laundry performance, intelligent fabric care and smart home connectivity for modern families in Saudi Arabia.\\n\\n• EXTRA-LARGE 15KG CAPACITY — Stainless-steel drum tackles king-size bedding and family loads in a single cycle, in an LG-standard depth chassis.\\n• AI DD® + 6 MOTION DD — AI Direct Drive senses load weight and fabric softness and auto-selects from six wash motions for superior care.\\n• TURBOWASH™ 39 + STEAM — Full wash-and-rinse in as little as 39 minutes. Allergy Care™ Steam cycle (BAF certified) reduces common household allergens.\\n• LG ThinQ® Wi-Fi + VOICE — Remote start, cycle monitoring, Smart Diagnosis™, and hands-free Alexa / Google Assistant control.\\n• QUIET & DURABLE — Inverter Direct Drive with vibration sensor for whisper-quiet operation; backed by LG\'s 10-year motor warranty.\\n\\nFinished in premium Essence White (Glossy) with a black-tinted tempered-glass door, clean LED display and intuitive dial + touch controls. Backed by LG Electronics\' official warranty and LG Saudi Arabia after-sales service for complete peace of mind.',
        'kw': 'LG WFN1510WHT 15kg Front Load Washing Machine AI DD 6 Motion DD Inverter Direct Drive Steam Allergy Care TurboWash 39 LG ThinQ Wi-Fi Smart Diagnosis Alexa Google Assistant Stainless Steel Drum Tempered Glass Door Essence White Glossy Saudi Arabia KSA Official LG 2025 Laundry Home Appliance'
    },
    'LS25CBBDIK': {
        'dv': 'HA', 'cat': 'Refrigerator', 'sub': 'Side by Side', 'ico': '❄️',
        'nm': 'LG 658L Side-by-Side Refrigerator with Smart Inverter Compressor — Dark Graphite Steel',
        'amz_title': 'LG 658L Side-by-Side Refrigerator with Smart Inverter Compressor, LINEAR Cooling, Deodorizer, Dark Graphite Steel, 10-Year Compressor Warranty (LS25CBBDIK)',
        'bul': [
            'EXPANSIVE 658L FAMILY CAPACITY — Side-by-side layout with 422L fresh-food and 206L freezer compartments keeps a full week of groceries organised, with three tempered-glass shelves in each side and two vegetable boxes for flexible, well-planned storage.',
            'SMART INVERTER COMPRESSOR — LG\'s BLDC Smart Inverter Compressor continuously adjusts cooling power to match real-time demand, delivering energy efficiency, quieter operation and the peace of mind of LG\'s 10-year compressor warranty.',
            'LINEAR COOLING™ — Precision temperature control minimises fluctuations inside the cabinet, helping vegetables, dairy and proteins stay fresher longer with reduced moisture loss and better nutrient preservation.',
            'HYGIENIC INTERIOR + TOP LED LIGHTING — Built-in Deodorizer neutralises mixed-food odours while top-mounted LED lighting illuminates every shelf clearly; Smart Diagnosis™ lets LG service quickly troubleshoot your fridge via phone or ThinQ® app.',
            'PREMIUM DARK GRAPHITE STEEL DESIGN — 913 × 1790 × 735 mm side-by-side footprint with durable PCM-finished Dark Graphite Steel doors fits modern kitchens elegantly, engineered by LG and backed by official LG Saudi Arabia warranty.'
        ],
        'amz_desc': 'Experience the LG 658L Side-by-Side Refrigerator (LS25CBBDIK) — engineered by LG to deliver exceptional cooling performance, energy efficiency and family-ready capacity for modern homes in Saudi Arabia.\\n\\n• EXPANSIVE 658L FAMILY CAPACITY — 422L refrigerator + 206L freezer with three tempered-glass shelves per side and two vegetable boxes.\\n• SMART INVERTER COMPRESSOR — Continuously modulates cooling power for energy efficiency, quiet operation and LG\'s 10-year compressor warranty.\\n• LINEAR COOLING™ — Precision temperature control keeps produce, dairy and proteins fresher for longer.\\n• HYGIENIC INTERIOR + LED — Built-in Deodorizer plus Top LED lighting across both compartments, with Smart Diagnosis™ for rapid after-sales support.\\n• PREMIUM DARK GRAPHITE STEEL DESIGN — 913 × 1790 × 735 mm side-by-side footprint in durable PCM Dark Graphite Steel finish.\\n\\nDesigned with LG\'s signature engineering, intuitive usability and trusted build quality. Backed by LG Electronics\' official warranty and LG Saudi Arabia after-sales service network for complete peace of mind.',
        'kw': 'LG LS25CBBDIK Side by Side Refrigerator 658L 23.2 Cu.Ft Smart Inverter Compressor BLDC LINEAR Cooling Deodorizer Dark Graphite Steel PCM Tempered Glass Shelves Vegetable Box Smart Diagnosis LG Saudi Arabia KSA 2025 Fridge Freezer Home Appliance'
    },
    'WFN1310WHT': {
        'dv': 'HA', 'cat': 'Washer', 'sub': 'Front Load', 'ico': '🧺',
        'nm': 'LG 13kg Front Load Washing Machine with AI DD® & Steam — Essence White (WFN1310WHT)',
        'amz_title': 'LG 13kg Front Load Washing Machine with AI DD®, Steam, TurboWash 360°, LG ThinQ Wi-Fi — Essence White, 10-Year Inverter Warranty (WFN1310WHT)',
        'bul': [
            'LARGE 13KG XL CAPACITY — Spacious stainless steel drum handles family-sized loads and bulky items like duvets, bedding and curtains in a single cycle — yet fits within LG\'s slim 645mm depth so it blends into any laundry space.',
            'AI DIRECT DRIVE® (AI DD®) TECHNOLOGY — Intelligent sensors weigh the load and assess fabric softness, then automatically select the optimal wash motion from LG\'s 6 Motion DD patterns for superior cleaning and gentle fabric care.',
            'TURBOWASH™ 360° + STEAM — TurboWash™ 360° sprays water in four directions to deliver a deep clean in just 39 minutes. Allergy Care™ with Steam reduces dust-mite, pet and pollen allergens plus household bacteria and fungi for healthier laundry.',
            'LG ThinQ® WI-FI SMART CONTROL — Start, monitor and control your washer from anywhere through the LG ThinQ® app. Download new cycles, track energy use, enjoy hands-free voice commands, and use Smart Diagnosis™ for instant support.',
            'QUIET INVERTER DIRECTDRIVE™ + 10-YEAR MOTOR WARRANTY — LG\'s Inverter DirectDrive motor with vibration sensor runs quieter and lasts longer, backed by a 10-year motor warranty. Premium Essence White glossy finish with black tinted tempered glass door.'
        ],
        'amz_desc': 'Experience the LG 13kg Front Load Washing Machine (WFN1310WHT) — engineered by LG to deliver intelligent fabric care, fast performance and smart home connectivity for modern families in Saudi Arabia.\\n\\n• LARGE 13KG XL CAPACITY — Stainless steel drum for big family loads and bulky bedding, in a slim 645mm standard-depth footprint.\\n• AI DD® TECHNOLOGY — 6 Motion DD + AI Direct Drive auto-selects the optimal wash motion for each fabric type.\\n• TURBOWASH™ 360° + STEAM — Deep clean in 39 minutes. Allergy Care™ with Steam reduces household allergens and bacteria.\\n• LG ThinQ® Wi-Fi — Remote start, cycle monitoring, downloadable cycles, voice control and Smart Diagnosis™.\\n• QUIET, DURABLE INVERTER DIRECTDRIVE™ — Vibration sensor and inverter motor deliver whisper-quiet operation; 10-year motor warranty.\\n\\nDesigned with LG\'s signature engineering, premium Essence White glossy finish and intuitive dial + touch LED controls. Backed by LG Electronics\' official warranty and LG Saudi Arabia after-sales service for complete peace of mind.',
        'kw': 'LG WFN1310WHT 13kg Front Load Washing Machine AI DD 6 Motion DD Inverter DirectDrive Steam Allergy Care TurboWash 360 39 Minutes LG ThinQ Wi-Fi Smart Diagnosis Stainless Steel Drum Tempered Glass Door Essence White Saudi Arabia KSA Official LG 2025 Laundry Home Appliance'
    },
    'WFN1310BST': {
        'dv': 'HA', 'cat': 'Washer', 'sub': 'Front Load', 'ico': '🧺',
        'nm': 'LG 13kg Front Load Washing Machine with AI DD® & Steam — Essense Graphite (WFN1310BST)',
        'amz_title': 'LG 13kg Front Load Washing Machine with AI DD®, Steam, TurboWash 360°, LG ThinQ Wi-Fi — Essense Graphite, 10-Year Inverter Warranty (WFN1310BST)',
        'bul': [
            'LARGE 13KG XL CAPACITY — Spacious stainless steel drum handles family-sized loads and bulky items like duvets, bedding and curtains in a single cycle — yet fits within LG\'s slim 645mm depth so it blends into any laundry space.',
            'AI DIRECT DRIVE® (AI DD®) TECHNOLOGY — Intelligent sensors weigh the load and assess fabric softness, then automatically select the optimal wash motion from LG\'s 6 Motion DD patterns for superior cleaning and gentle fabric care.',
            'TURBOWASH™ 360° + STEAM — TurboWash™ 360° sprays water in four directions to deliver a deep clean in just 39 minutes. Allergy Care™ with Steam reduces dust-mite, pet and pollen allergens plus household bacteria and fungi for healthier laundry.',
            'LG ThinQ® WI-FI SMART CONTROL — Start, monitor and control your washer from anywhere through the LG ThinQ® app. Download new cycles, track energy use, enjoy hands-free voice commands, and use Smart Diagnosis™ for instant support.',
            'QUIET INVERTER DIRECTDRIVE™ + 10-YEAR MOTOR WARRANTY — LG\'s Inverter DirectDrive motor with vibration sensor runs quieter and lasts longer, backed by a 10-year motor warranty. Premium Essense Graphite finish with black tinted tempered glass door.'
        ],
        'amz_desc': 'Experience the LG 13kg Front Load Washing Machine (WFN1310BST) — engineered by LG to deliver intelligent fabric care, fast performance and smart home connectivity for modern families in Saudi Arabia, finished in premium Essense Graphite.\\n\\n• LARGE 13KG XL CAPACITY — Stainless steel drum for big family loads and bulky bedding, in a slim 645mm standard-depth footprint.\\n• AI DD® TECHNOLOGY — 6 Motion DD + AI Direct Drive auto-selects the optimal wash motion for each fabric type.\\n• TURBOWASH™ 360° + STEAM — Deep clean in 39 minutes. Allergy Care™ with Steam reduces household allergens and bacteria.\\n• LG ThinQ® Wi-Fi — Remote start, cycle monitoring, downloadable cycles, voice control and Smart Diagnosis™.\\n• QUIET, DURABLE INVERTER DIRECTDRIVE™ — Vibration sensor and inverter motor deliver whisper-quiet operation; 10-year motor warranty.\\n\\nDesigned with LG\'s signature engineering, premium Essense Graphite finish and intuitive dial + touch LED controls. Backed by LG Electronics\' official warranty and LG Saudi Arabia after-sales service for complete peace of mind.',
        'kw': 'LG WFN1310BST 13kg Front Load Washing Machine AI DD 6 Motion DD Inverter DirectDrive Steam Allergy Care TurboWash 360 39 Minutes LG ThinQ Wi-Fi Smart Diagnosis Stainless Steel Drum Tempered Glass Door Essense Graphite Black Saudi Arabia KSA Official LG 2025 Laundry Home Appliance'
    },
    'S65TR': {
        'dv': 'MS', 'cat': 'Audio', 'sub': 'Soundbar', 'ico': '🔈',
        'nm': 'LG Soundbar S65TR — 5.1ch Home Cinema with Wireless Subwoofer and Rear Speakers (420W)',
        'amz_title': 'LG Soundbar S65TR — 5.1ch Home Cinema System, 420W, Wireless Subwoofer + Wireless Rear Speakers, AI Sound Pro, WOW Orchestra for LG TVs, Bluetooth, HDMI eARC',
        'bul': [
            'COMPLETE 5.1-CHANNEL HOME CINEMA — Main soundbar + wireless subwoofer + two wireless rear speakers deliver a fully immersive 420W 5.1-channel surround experience that pulls you into every movie, match and music session.',
            'WIRELESS SUBWOOFER + WIRELESS REAR SPEAKERS — All satellites connect wirelessly to the main soundbar, so only the power cables are visible. Set up a cinema-grade surround system in minutes without drilling walls or routing audio cables.',
            'AI SOUND PRO — LG\'s AI automatically detects whether you\'re watching a movie, enjoying music or listening to speech and applies the optimal audio profile in real time — no manual adjustment required.',
            'WOW ORCHESTRA + WOW INTERFACE (LG TV) — Pair with a compatible LG TV to play TV and soundbar speakers together for richer, bigger sound via WOW Orchestra. WOW Interface integrates soundbar control directly into the LG TV menu.',
            'BUILT FOR THE PLANET, BUILT TO LAST — Internal components made with recycled plastic and the front grill is woven from recycled plastic bottles. HDMI eARC + Bluetooth + Optical connectivity; controllable via LG ThinQ™ app; backed by official LG Saudi Arabia warranty.'
        ],
        'amz_desc': 'Experience the LG Soundbar S65TR — a true 5.1-channel home cinema system engineered by LG to transform any living room into a premium audio space.\\n\\n• COMPLETE 5.1-CHANNEL SYSTEM — Main soundbar, wireless subwoofer, and two wireless rear speakers deliver 420W of total power and enveloping surround sound.\\n• WIRELESS REAR + SUBWOOFER — Minimal cable clutter, quick setup. Only power cables required.\\n• AI SOUND PRO — Automatically tunes audio for Movies, Music or Voice in real time.\\n• WOW ORCHESTRA + WOW INTERFACE — Pairs beautifully with LG TVs for synchronised playback and single-remote control.\\n• SUSTAINABLY BUILT — Internal recycled plastic + grill fabric made from recycled plastic bottles.\\n• CONNECTIVITY — HDMI eARC, HDMI in, Optical, Bluetooth 5.0, LG Sound Sync, LG ThinQ™ app support.\\n\\nDesigned with LG\'s signature engineering, the S65TR combines cinematic audio, wireless convenience and sustainable materials in one package. Backed by LG Electronics\' official warranty and LG Saudi Arabia after-sales service.',
        'kw': 'LG S65TR Soundbar 5.1 Channel Home Cinema Surround Sound Wireless Subwoofer Wireless Rear Speakers 420W AI Sound Pro WOW Orchestra WOW Interface Dolby Digital DTS Bluetooth HDMI eARC Optical LG ThinQ Recycled Plastic Saudi Arabia KSA Official LG Home Theater Audio'
    },
    'S20A': {
        'dv': 'MS', 'cat': 'Audio', 'sub': 'Soundbar', 'ico': '🔈',
        'nm': 'LG Soundbar S20A — 2.1ch Compact Soundbar with Built-in Subwoofers, AI Sound Pro, Bluetooth',
        'amz_title': 'LG Soundbar S20A — 2.1ch Compact Soundbar, 100W, Built-in Subwoofers, AI Sound Pro, WOW Orchestra for LG TVs, Bluetooth 5.1, Optical, LG ThinQ App',
        'bul': [
            'COMPACT 2.1-CHANNEL SOUNDBAR, NO SEPARATE SUB NEEDED — Built-in subwoofers with double tweeters and a passive radiator deliver clear, balanced 100W room-filling sound — all from a single slim bar that tucks neatly below any TV.',
            'AI SOUND PRO — Intelligently detects whether you\'re watching a movie, listening to music or following dialogue, then automatically applies the optimal audio profile in real time so every scene sounds just right.',
            'WOW ORCHESTRA + WOW INTERFACE FOR LG TVs — Pair with a compatible LG TV to play TV and soundbar speakers together (WOW Orchestra) for a richer soundstage, and control the soundbar directly from your LG TV remote (WOW Interface).',
            'LG ThinQ® APP CONTROL + SMART CONNECTIVITY — Adjust volume, sound modes and settings from your phone via the LG ThinQ® app. Bluetooth 5.1, Optical input, and HDMI-compatible connections make set-up simple for any TV or device.',
            'SLEEK, SUSTAINABLE DESIGN — Slim low-profile 820mm-wide chassis in premium black blends into any living room. Built with recycled resin as part of LG\'s ESG commitment to more sustainable audio products. Backed by LG Saudi Arabia official warranty.'
        ],
        'amz_desc': 'Experience the LG Soundbar S20A — a compact, premium standalone soundbar engineered by LG to deliver room-filling 2.1-channel sound without the clutter of a separate subwoofer.\\n\\n• COMPACT 2.1-CHANNEL — Built-in subwoofers, double tweeters and passive radiator deliver 100W of balanced audio from a single slim bar.\\n• AI SOUND PRO — Auto-tunes audio for Music, Voice or Cinema in real time.\\n• WOW ORCHESTRA + WOW INTERFACE — Seamless pairing with LG TVs for unified playback and single-remote control.\\n• SMART APP CONTROL — LG ThinQ® app support, Bluetooth 5.1, Optical input, and USB connection.\\n• SUSTAINABLE BUILD — Made with recycled resin as part of LG\'s ESG commitment.\\n\\nSleek low-profile design in premium black fits beautifully below any TV. Backed by LG Electronics\' official warranty and LG Saudi Arabia after-sales service network for complete peace of mind.',
        'kw': 'LG S20A Soundbar 2.1 Channel Compact Standalone Built-in Subwoofers 100W AI Sound Pro WOW Orchestra WOW Interface LG ThinQ Bluetooth 5.1 Optical Dolby Digital DTS Recycled Resin Black Saudi Arabia KSA Official LG TV Audio Home Entertainment'
    },
    'WFR1114MB': {
        'dv': 'HA', 'cat': 'Washer', 'sub': 'Front Load', 'ico': '🧺',
        'nm': 'LG 11kg Slim Front Load Washing Machine with AI DD™ & Steam — Middle Black (WFR1114MB)',
        'amz_title': 'LG 11kg Slim Front Load Washing Machine with AI DD™, Steam (99.9% Allergen Removal), TurboWash™ 59-min, LG ThinQ Wi-Fi — Middle Black (WFR1114MB)',
        'bul': [
            '11KG CAPACITY IN A SLIM 565MM FOOTPRINT — Generous 11kg stainless-steel drum fits into a compact 600 × 850 × 565 mm body — perfect for family loads in urban apartments and modern laundry spaces where depth is limited.',
            'AI DIRECT DRIVE® (AI DD™) — Intelligently senses both load weight and fabric softness, then auto-selects the optimal wash motion from LG\'s 6 Motion DD patterns — delivering up to 18% more fabric protection for long-lasting garments.',
            'STEAM™ HYGIENE — 99.9% ALLERGEN REMOVAL — LG Steam™ eliminates up to 99.9% of dust-mite, pollen and pet allergens while also reducing wrinkles by 30% during the tumble cycle — ideal for families with sensitive skin or allergy sufferers.',
            'TURBOWASH™ 59 + SPEED 14 — Wash a full load in just 59 minutes with TurboWash™, or a small top-up load in 14 minutes with Speed 14 — so laundry never slows down your day. AI Wash automatically picks the best cycle for you.',
            'LG ThinQ® Wi-Fi + INVERTER DIRECTDRIVE™ 10-YEAR WARRANTY — Remote start, cycle monitoring, downloadable programs, Smart Diagnosis™ and energy tracking via the LG ThinQ® app. Quiet Inverter DirectDrive motor backed by 10-year warranty. Premium Middle Black finish with black tinted tempered glass door.'
        ],
        'amz_desc': 'Experience the LG 11kg Slim Front Load Washing Machine (WFR1114MB) — engineered by LG to deliver intelligent fabric care, fast cleaning and smart connectivity in a compact body designed for modern Saudi homes.\\n\\n• 11KG IN A SLIM 565MM DEPTH — Compact 600 × 850 × 565 mm footprint fits neatly into smaller laundry spaces without sacrificing capacity.\\n• AI DD™ TECHNOLOGY — Senses fabric weight and softness, auto-selects optimal wash motion for up to 18% more fabric protection.\\n• STEAM™ — 99.9% allergen removal + 30% less wrinkles, tested by Intertek and TÜV Rheinland.\\n• TURBOWASH™ 59 + SPEED 14 — Full load in 59 minutes, small top-up loads in 14 minutes.\\n• LG ThinQ® Wi-Fi — Remote start, cycle monitoring, downloadable cycles, voice support and Smart Diagnosis™.\\n• QUIET INVERTER DIRECTDRIVE™ — 10-year motor warranty, vibration sensor, foam detection, Stainless Steel Drum with Slim Lifter.\\n\\nDesigned with LG\'s signature engineering and premium Middle Black finish with black tinted tempered glass door. Backed by LG Electronics\' official warranty and LG Saudi Arabia after-sales service network for complete peace of mind.',
        'kw': 'LG WFR1114MB 11kg Slim Front Load Washing Machine AI DD 6 Motion DD Inverter DirectDrive Steam 99.9% Allergen Removal TurboWash 59 Speed 14 Minute LG ThinQ Wi-Fi Smart Diagnosis Stainless Steel Drum Tempered Glass Door Middle Black Saudi Arabia KSA Official LG Compact Apartment Laundry'
    },
    'A9K-SOLO': {
        'dv': 'HA', 'cat': 'Vacuum', 'sub': 'Cordless Stick', 'ico': '🧹',
        'nm': 'LG CordZero™ A9 Kompressor Cordless Stick + Handheld Vacuum — Fantasy Silver (A9K-SOLO)',
        'amz_title': 'LG CordZero™ A9 Kompressor Cordless Vacuum A9K-SOLO — 220W, 2-in-1 Stick+Handheld, Kompressor Tech, Smart Inverter Motor (10-Yr), 5-Step Filtration, ThinQ Wi-Fi',
        'bul': [
            'KOMPRESSOR™ TECHNOLOGY — LG\'s exclusive Kompressor™ mechanism compresses dust and hair in the bin by up to 2.4× the uncompressed capacity, so you empty far less often. Release the lever, open the door, and waste drops straight out — completely hands-free hygienic disposal.',
            '220W POWERFUL SUCTION + SMART INVERTER MOTOR™ — Brushless Smart Inverter Motor™ paired with the Axial Turbo Cyclone delivers powerful, long-lasting 220W suction — and LG backs the motor with a 10-year warranty for worry-free ownership.',
            '2-IN-1 STICK + HANDHELD, 60-MIN RUN TIME — Lightweight 2.9kg body converts from full stick vacuum to handheld in seconds for cars, sofas and high shelves. One lithium-ion battery delivers up to 60 minutes in Normal mode and 240-minute full recharge.',
            '5-STEP FILTRATION + WASHABLE FILTERS — Advanced 5-step cyclonic filtration captures an average 99.999% of 0.5-4.2 μm fine dust particles. All three filters (metal, cloth pre-filter, fine dust) are fully washable under water — no replacement costs.',
            'SMART THINQ® CONTROL + NO-DRILL 3-IN-1 STAND — Monitor filter status, battery level and cleaning history from your smartphone via LG ThinQ®. Included charging stand offers three storage options (self-standing / compact / wall-mount) without drilling. Thumb-operated controls make mode switching effortless.'
        ],
        'amz_desc': 'Experience the LG CordZero™ A9 Kompressor (A9K-SOLO) — a premium 2-in-1 cordless stick + handheld vacuum engineered by LG for deep, effortless cleaning in modern Saudi homes.\\n\\n• KOMPRESSOR™ TECHNOLOGY — Compresses dust and hair in the bin by up to 2.4×; you empty less often and hands-free.\\n• 220W POWERFUL SUCTION — Smart Inverter Motor™ (brushless, 10-year warranty) + Axial Turbo Cyclone.\\n• 60 MINUTES RUN TIME — One lithium-ion battery, 240-minute recharge, Normal / Power / Turbo modes.\\n• 2-IN-1 VERSATILITY — Converts stick to handheld in seconds; telescopic wand, thumb controls.\\n• 5-STEP FILTRATION — 99.999% fine dust capture; fully washable filters.\\n• 3-IN-1 CHARGING STAND — Self-standing / compact / wall-mount storage, no drilling needed.\\n• SMART LG ThinQ® — Filter + battery alerts, cleaning history, Smart Diagnosis™.\\n\\nFinished in elegant Fantasy Silver. Included: main unit, Power Drive Nozzle, Combination Tool, Crevice Tool, 3-in-1 charging stand. Backed by LG\'s official warranty and LG Saudi Arabia after-sales service.',
        'kw': 'LG A9K-SOLO CordZero A9 Kompressor Cordless Stick Vacuum Handheld 2-in-1 220W Smart Inverter Motor 10 Year Warranty Lithium-ion Battery 60 Minutes 5-Step Filtration Washable Filters Kompressor Technology LG ThinQ Wi-Fi Fantasy Silver Saudi Arabia KSA Official LG Floor Carpet Pet Home Cleaning'
    },
    'LS19GBBDI': {
        'dv': 'HA', 'cat': 'Refrigerator', 'sub': 'Side by Side', 'ico': '❄️',
        'nm': 'LG 17.9 Cu.Ft Side-by-Side Refrigerator with Smart Inverter Compressor — Silver (LS19GBBDI)',
        'amz_title': 'LG 17.9 Cu.Ft (~510L) Side-by-Side Refrigerator with Smart Inverter Compressor, LINEAR Cooling™, SASO-Certified, 10-Year Compressor Warranty — Silver (LS19GBBDI)',
        'bul': [
            'SPACIOUS 17.9 CU.FT (~510L) SIDE-BY-SIDE LAYOUT — Generous capacity organises groceries neatly across fresh-food and freezer compartments, with well-planned shelves for weekly family shopping and easy-reach access on both sides.',
            'SMART INVERTER COMPRESSOR (10-YEAR WARRANTY) — LG\'s BLDC Smart Inverter Compressor adjusts cooling power continuously to match real-time demand, delivering energy efficiency, quieter operation and long-lasting reliability.',
            'LINEAR COOLING™ FOR LASTING FRESHNESS — Precision temperature control minimises fluctuations inside the cabinet, helping vegetables, dairy and proteins stay fresher longer with reduced moisture loss.',
            'PREMIUM SILVER FINISH — Sleek Silver PCM door finish with ergonomic handles complements modern kitchens, while the side-by-side door design makes every shelf easy to reach without bending down.',
            'SASO-CERTIFIED + SMART DIAGNOSIS™ — Certified by SASO for Saudi Arabia energy compliance. Smart Diagnosis™ lets LG service technicians troubleshoot your fridge quickly via phone for minimum downtime. Backed by LG Saudi Arabia official warranty.'
        ],
        'amz_desc': 'Experience the LG 17.9 Cu.Ft Side-by-Side Refrigerator (LS19GBBDI) — engineered by LG to deliver dependable everyday cooling, generous family capacity and energy-efficient operation for modern Saudi homes.\\n\\n• 17.9 CU.FT (~510L) CAPACITY — Spacious side-by-side layout for organised grocery storage.\\n• SMART INVERTER COMPRESSOR — Continuous cooling modulation, quiet operation, 10-year warranty.\\n• LINEAR COOLING™ — Precision temperature control keeps produce fresh longer.\\n• PREMIUM SILVER FINISH — Sleek PCM door treatment complements any kitchen.\\n• SASO-CERTIFIED — Meets Saudi Arabia energy efficiency requirements; includes Smart Diagnosis™ for rapid after-sales support.\\n\\nBacked by LG Electronics\' official warranty and LG Saudi Arabia after-sales service network for complete peace of mind.',
        'kw': 'LG LS19GBBDI Side by Side Refrigerator 17.9 Cu.Ft 510L Smart Inverter Compressor BLDC LINEAR Cooling Silver PCM SASO Smart Diagnosis 10 Year Warranty Saudi Arabia KSA Official LG Fridge Freezer Home Appliance'
    },
    'DFC435FW': {
        'dv': 'HA', 'cat': 'DW', 'sub': 'Dishwasher', 'ico': '🍽️',
        'nm': 'LG 14-Place Dishwasher with TrueSteam™, QuadWash™, Inverter Direct Drive, LG ThinQ — White (DFC435FW)',
        'amz_title': 'LG 14-Place Dishwasher DFC435FW — TrueSteam™, QuadWash™ (4-Spray Arms), Inverter Direct Drive (43dBA, 10-Yr Warranty), EasyRack™ Plus, Auto Open Dry, LG ThinQ Wi-Fi',
        'bul': [
            '14-PLACE CAPACITY + QUADWASH™ 4-ARM COVERAGE — Fits a full family dinner load (14 place settings) into a standard 600mm-wide body. QuadWash™ uses four multi-directional spray arms (vs typical 2) with high-pressure jets to clean every corner, first time, every time.',
            'TRUESTEAM™ — SPARKLING DISHES, 30% LESS WATER SPOTS — Pure-water steam particles reach every dish surface for sparkling-clean results and up to 30% fewer water spots. High Temp rinse reaches 80°C for hygienic care of delicate glassware, baby bottles and heavy-soil pots.',
            'INVERTER DIRECT DRIVE MOTOR — 43 dBA WHISPER-QUIET + 10-YEAR WARRANTY — LG\'s brushless Inverter Direct Drive Motor runs at a class-leading 43 dBA (Class B) with long-lasting reliability. Backed by LG\'s 10-year motor warranty.',
            'EASYRACK™ PLUS + AUTO OPEN DRY — Foldable tines, 3-level height-adjustable upper rack, and a dedicated 3rd rack for long flatware make loading flexible. Auto Open Dry opens the door automatically at cycle end, letting humidity escape for superior drying.',
            'LG ThinQ® Wi-Fi + SMART DIAGNOSIS™ — Download new wash cycles (Pots & Pans, Casseroles, Glassware, Night Care), monitor progress remotely, and troubleshoot instantly through LG ThinQ® app. Machine Clean Reminder every 30 cycles keeps your dishwasher fresh.'
        ],
        'amz_desc': 'Experience the LG 14-Place Dishwasher (DFC435FW) — engineered by LG to deliver powerful cleaning, steam hygiene and smart connectivity in an elegant, whisper-quiet design for modern Saudi homes.\\n\\n• 14-PLACE CAPACITY — Fits a full family dinner load in a standard 600 × 850 × 600 mm body.\\n• QUADWASH™ — 4 multi-directional spray arms for complete coverage.\\n• TRUESTEAM™ — Sparkling dishes, 30% less water spots, up to 80°C High Temp rinse.\\n• INVERTER DIRECT DRIVE MOTOR — 43 dBA whisper-quiet operation, 10-year warranty.\\n• EASYRACK™ PLUS — Foldable tines, height-adjustable upper rack, 3rd rack for long flatware.\\n• AUTO OPEN DRY — Door opens automatically for superior drying.\\n• 10 CYCLES + 8 OPTIONS — Auto, Eco, Intensive, Delicate, Express (38 min), Turbo (59 min), Half Load, Dual Zone, High Temp, Download Cycle.\\n• LG ThinQ® Wi-Fi — Remote monitoring, downloadable cycles, Smart Diagnosis™.\\n• SAFETY — Aqua-Stop leak protection, Anti-Bacterial Treatment, Control Lock.\\n\\n9.5 L water consumption per cycle. Sleek White exterior with Micro LED display. Backed by LG Electronics\' official warranty and LG Saudi Arabia after-sales service.',
        'kw': 'LG DFC435FW Dishwasher 14 Place Settings TrueSteam QuadWash EasyRack Plus Inverter Direct Drive Motor 43dBA Auto Open Dry Aqua-Stop Water Softener LG ThinQ Wi-Fi Smart Diagnosis White 10 Year Warranty Saudi Arabia KSA Official LG Kitchen Home Appliance Dish Washer'
    },
    'WFR1114WH': {
        'dv': 'HA', 'cat': 'Washer', 'sub': 'Front Load', 'ico': '🧺',
        'nm': 'LG 11kg Slim Front Load Washing Machine with AI DD™ & Steam — White (WFR1114WH)',
        'amz_title': 'LG 11kg Slim Front Load Washing Machine with AI DD™, Steam (99.9% Allergen Removal), TurboWash™ 59-min, LG ThinQ Wi-Fi — White (WFR1114WH)',
        'bul': [
            '11KG CAPACITY IN A SLIM 565MM FOOTPRINT — Generous 11kg stainless-steel drum fits into a compact 600 × 850 × 565 mm body — perfect for family loads in urban apartments and modern laundry spaces where depth is limited.',
            'AI DIRECT DRIVE® (AI DD™) TECHNOLOGY — Intelligently senses both load weight and fabric softness, then auto-selects the optimal wash motion from LG\'s 6 Motion DD patterns — delivering up to 18% more fabric protection for long-lasting garments.',
            'STEAM™ HYGIENE — 99.9% ALLERGEN REMOVAL — LG Steam™ eliminates up to 99.9% of dust-mite, pollen and pet allergens while also reducing wrinkles by 30% during the tumble cycle — ideal for families with sensitive skin or allergy sufferers.',
            'TURBOWASH™ 59 + SPEED 14 — Wash a full load in just 59 minutes with TurboWash™, or a small top-up load in 14 minutes with Speed 14 — so laundry never slows down your day. AI Wash automatically picks the best cycle for you.',
            'LG ThinQ® Wi-Fi + INVERTER DIRECTDRIVE™ 10-YEAR WARRANTY — Remote start, cycle monitoring, downloadable programs, Smart Diagnosis™ and energy tracking via the LG ThinQ® app. Quiet Inverter DirectDrive motor backed by 10-year warranty. Classic White finish with black tinted tempered glass door.'
        ],
        'amz_desc': 'Experience the LG 11kg Slim Front Load Washing Machine (WFR1114WH) — engineered by LG to deliver intelligent fabric care, fast cleaning and smart connectivity in a compact body designed for modern Saudi homes, finished in timeless White.\\n\\n• 11KG IN A SLIM 565MM DEPTH — Compact 600 × 850 × 565 mm footprint fits neatly into smaller laundry spaces without sacrificing capacity.\\n• AI DD™ TECHNOLOGY — Senses fabric weight and softness, auto-selects optimal wash motion for up to 18% more fabric protection.\\n• STEAM™ — 99.9% allergen removal + 30% less wrinkles, tested by Intertek and TÜV Rheinland.\\n• TURBOWASH™ 59 + SPEED 14 — Full load in 59 minutes, small top-up loads in 14 minutes.\\n• LG ThinQ® Wi-Fi — Remote start, cycle monitoring, downloadable cycles, voice support and Smart Diagnosis™.\\n• QUIET INVERTER DIRECTDRIVE™ — 10-year motor warranty, vibration sensor, foam detection, Stainless Steel Drum with Slim Lifter.\\n\\nClassic White finish with black tinted tempered glass door — a timeless look that fits every kitchen or utility room. Backed by LG Electronics\' official warranty and LG Saudi Arabia after-sales service network for complete peace of mind.',
        'kw': 'LG WFR1114WH 11kg Slim Front Load Washing Machine AI DD 6 Motion DD Inverter DirectDrive Steam 99.9% Allergen Removal TurboWash 59 Speed 14 Minute LG ThinQ Wi-Fi Smart Diagnosis Stainless Steel Drum Tempered Glass Door White Saudi Arabia KSA Official LG Compact Apartment Laundry'
    },
    'WSV0906XM': {
        'dv': 'HA', 'cat': 'Washer', 'sub': 'Combo', 'ico': '🧺',
        'nm': 'LG 9kg Washer + 6kg Dryer Combo with AI DD™ & Steam — Front Load All-in-One, Stainless Silver (WSV0906XM)',
        'amz_title': 'LG 9kg Washer + 6kg Dryer All-in-One Combo with AI DD™, Steam (99.9% Allergen Removal), Full Stainless Drum, LG ThinQ Wi-Fi — Stainless Silver (WSV0906XM)',
        'bul': [
            'ALL-IN-ONE WASHER + DRYER IN ONE UNIT — 9kg wash capacity + 6kg dry capacity in a single front-load combo saves valuable floor space. Go from soiled laundry to ready-to-wear clothes without transferring loads between two separate machines — ideal for apartments and compact laundry rooms.',
            'AI DIRECT DRIVE® (AI DD™) — Intelligent sensors weigh the load and detect fabric softness, then auto-select the optimal wash motion from LG\'s 6 Motion DD patterns — up to 18% more fabric protection for long-lasting garment care.',
            'STEAM™ HYGIENE — 99.9% ALLERGEN REMOVAL — LG Steam™ eliminates up to 99.9% of dust-mite, pollen and pet allergens — tested by TÜV Rheinland. Ideal for families with sensitive skin, asthma sufferers, and pet owners.',
            'FULL STAINLESS STEEL DRUM + INVERTER DIRECTDRIVE™ — Hygienic Full Stainless interior with a stainless slim lifter stands up to years of daily use. Inverter DirectDrive motor with vibration sensor runs quieter and lasts longer, backed by LG\'s 10-year motor warranty.',
            'LG ThinQ® Wi-Fi SMART CONTROL — Start and monitor wash/dry cycles remotely from your smartphone via the LG ThinQ® app. Download new cycles, track energy usage, and use Smart Diagnosis™ for instant troubleshooting. Premium Stainless Silver finish with Touch LED display.'
        ],
        'amz_desc': 'Experience the LG 9kg Washer + 6kg Dryer All-in-One Combo (WSV0906XM) — engineered by LG to deliver complete wash-and-dry convenience in a single compact front-load unit for modern Saudi homes.\\n\\n• ALL-IN-ONE WASHER + DRYER — 9kg wash / 6kg dry in a single 600 × 850 × 620 mm unit; no separate dryer required.\\n• AI DD™ — 18% more fabric protection via intelligent motion selection.\\n• STEAM™ — 99.9% allergen removal, tested by TÜV Rheinland.\\n• FULL STAINLESS DRUM — Hygienic, long-lasting drum with Slim Stainless Lifter.\\n• INVERTER DIRECTDRIVE™ — Quiet, durable motor with 10-year warranty.\\n• LG ThinQ® Wi-Fi — Remote start, cycle monitoring, downloadable cycles, Smart Diagnosis™.\\n• TOUCH LED DISPLAY — Intuitive programme selection.\\n\\nFinished in premium Stainless Silver. Backed by LG Electronics\' official warranty and LG Saudi Arabia after-sales service network for complete peace of mind.',
        'kw': 'LG WSV0906XM Washer Dryer Combo 9kg Wash 6kg Dry All-in-One Front Load AI DD 6 Motion DD Inverter DirectDrive Steam 99.9% Allergen Removal Full Stainless Steel Drum LG ThinQ Wi-Fi Smart Diagnosis Stainless Silver Saudi Arabia KSA Official LG Apartment Compact Laundry'
    },
    'RH18U8JVCW': {
        'dv': 'HA', 'cat': 'Dryer', 'sub': 'Heat Pump', 'ico': '🌀',
        'nm': 'LG 18kg DUAL Inverter Heat Pump™ Dryer with Eco Hybrid™, Allergy Care, LG ThinQ — Black Steel (RH18U8JVCW)',
        'amz_title': 'LG 18kg DUAL Inverter Heat Pump™ Dryer RH18U8JVCW — Eco Hybrid™, Allergy Care (99.9% Dust-Mite Reduction, BAF Certified), Auto Cleaning Condenser, LG ThinQ Wi-Fi',
        'bul': [
            'XL 18KG HEAT PUMP CAPACITY — Massive 18kg drum handles family-sized loads and bulky bedding in a single cycle. DUAL Inverter Heat Pump™ delivers both higher energy efficiency AND shorter drying times than conventional dryers — lower bills, less waiting.',
            'ECO HYBRID™ — SAVE ENERGY OR SAVE TIME — Switch between maximum efficiency mode for lowest power use, or fast-dry mode when you\'re in a hurry. One dryer, two modes, tailored to your day.',
            'GENTLE CARE + SENSOR DRY — Low-temperature Heat Pump technology smoothens creases and reduces shrinkage to protect delicate fabrics. Intelligent Sensor Dry detects real-time moisture levels and auto-adjusts drying time — no over-drying, no dampness.',
            'ALLERGY CARE — 99.9% DUST-MITE REDUCTION (BAF CERTIFIED) — The Allergy Care cycle reduces 99.9% of live house dust mites — tested and certified by the British Allergy Foundation. Ideal for families with sensitive skin, asthma and pet allergies.',
            'LG ThinQ® WI-FI + DUAL 10-YEAR WARRANTY — Remote start, cycle monitoring, downloadable cycles (Gym Clothes, Blanket Refresh, Lingerie, Minimise Wrinkles), energy tracking and Smart Diagnosis™ via LG ThinQ® app. Backed by LG\'s DUAL 10-Year warranty on BOTH the Inverter Compressor AND the Inverter Motor. Ventless Condenser operation, Auto Cleaning Condenser, Dual Lint Filter — Black Steel finish with tempered glass door.'
        ],
        'amz_desc': 'Experience the LG 18kg DUAL Inverter Heat Pump™ Dryer (RH18U8JVCW) — LG\'s premium ventless heat pump dryer engineered for XL family laundry, superior energy efficiency and hypoallergenic drying, for modern Saudi homes.\\n\\n• XL 18KG CAPACITY — Handles family loads and bulky bedding in one cycle.\\n• DUAL INVERTER HEAT PUMP™ — Higher efficiency + faster drying than conventional dryers.\\n• ECO HYBRID™ — Choose energy-save or time-save mode to fit your day.\\n• GENTLE CARE + SENSOR DRY — Low-temp drying protects fabrics; sensors auto-optimise cycle time.\\n• ALLERGY CARE — 99.9% dust-mite reduction, BAF-certified.\\n• AUTO CLEANING CONDENSER + DUAL LINT FILTER — Self-maintaining for consistent performance.\\n• LG ThinQ® Wi-Fi — Remote start, downloadable cycles, Smart Diagnosis™.\\n• DUAL 10-YEAR WARRANTY — Compressor AND Motor both covered.\\n• VENTLESS CONDENSER DESIGN — No external venting required; installs anywhere with power.\\n\\nPremium Black Steel finish with Black Tinted Tempered Glass Door. Backed by LG Electronics\' official warranty and LG Saudi Arabia after-sales service network.',
        'kw': 'LG RH18U8JVCW Dryer 18kg DUAL Inverter Heat Pump Eco Hybrid Gentle Care Sensor Dry Allergy Care 99.9% Dust Mite BAF Certified Auto Cleaning Condenser Dual Lint Filter AI DD 6 Motion DD Inverter DirectDrive LG ThinQ Wi-Fi Smart Diagnosis Ventless Condenser Black Steel Tempered Glass 10 Year Warranty Saudi Arabia KSA Official LG'
    },
    'S95TR': {
        'dv': 'MS', 'cat': 'Audio', 'sub': 'Soundbar', 'ico': '🔈',
        'nm': 'LG Soundbar S95TR — 9.1.5ch Flagship Home Cinema (810W) with Dolby Atmos, DTS:X, WOWCAST, LG ThinQ',
        'amz_title': 'LG Soundbar S95TR — 9.1.5ch Flagship Home Cinema, 810W, Dolby Atmos + DTS:X, Wireless Sub + Wireless Rear Speakers (6ch), WOWCAST, WOW Orchestra for LG TVs',
        'bul': [
            'FLAGSHIP 9.1.5-CHANNEL HOME CINEMA (810W) — 9 front/side channels + 1 wireless subwoofer + 5 up-firing channels delivering 810W of total power. The ultimate Dolby Atmos and DTS:X experience in your living room — main soundbar + wireless subwoofer + 2 wireless rear speakers.',
            '6-CHANNEL WIRELESS REAR SPEAKERS — Each rear speaker contains 3 drivers (1 side-firing + 2 up-firing) for a total 6-channel rear array. Only a single power cable per speaker is required — wireless sound signal comes from the main soundbar for clutter-free cinema.',
            'AI ROOM CALIBRATION PRO + AI SOUND PRO — AI Room Calibration Pro measures your room\'s acoustics and auto-tunes the soundbar for distortion-free playback in YOUR space. AI Sound Pro detects the genre in real time and applies the ideal audio profile for movies, music, sports or news.',
            'WOWCAST + WOW ORCHESTRA + WOW INTERFACE — WOWCAST sends lossless multi-channel audio from your LG TV wirelessly to the soundbar. WOW Orchestra plays TV + soundbar speakers in harmony for expanded sound. WOW Interface puts soundbar control in your LG TV remote.',
            'UNIVERSAL STREAMING + SUSTAINABLE BUILD — Apple AirPlay 2, Amazon Alexa, Google Home, Spotify Connect, TIDAL Connect, Google Cast, LG ThinQ™, Bluetooth 5.1. HDMI eARC. Built with recycled plastic internals, recycled-PET polyester grill fabric, and recycled pulp packaging. Backed by LG Saudi Arabia warranty.'
        ],
        'amz_desc': 'Experience the LG Soundbar S95TR — LG\'s flagship 9.1.5-channel home cinema system engineered by LG to deliver uncompromising cinematic sound, seamless LG TV integration, and universal smart-home compatibility.\\n\\n• 9.1.5 CHANNELS / 810W — Main soundbar + wireless subwoofer + 2 wireless 3-driver rear speakers (6ch rear array).\\n• DOLBY ATMOS + DTS:X — Full object-based 3D surround sound with 5 up-firing channels for true height effects.\\n• AI ROOM CALIBRATION PRO — Auto-tunes to your specific room acoustics.\\n• AI SOUND PRO — Real-time genre detection and audio profile tuning.\\n• WOWCAST / WOW ORCHESTRA / WOW INTERFACE — Wireless lossless multi-channel from LG TV; unified playback; single-remote control.\\n• UNIVERSAL STREAMING — Apple AirPlay 2, Amazon Alexa, Google Home, Spotify Connect, TIDAL Connect, Google Cast, LG ThinQ™.\\n• CONNECTIVITY — 2× HDMI in, 1× HDMI eARC out, Optical, USB, Bluetooth 5.1, Wi-Fi.\\n• HIGH-RES AUDIO — 24-bit / 96 kHz support.\\n• SUSTAINABLE BUILD — Recycled plastic internals, recycled-PET polyester jersey grill, recycled pulp packaging.\\n\\nBacked by LG Electronics\' official warranty and LG Saudi Arabia after-sales service network for complete peace of mind.',
        'kw': 'LG S95TR Flagship Soundbar 9.1.5 Channel 810W Home Cinema Dolby Atmos DTS:X Wireless Subwoofer Wireless Rear Speakers 6 Channel Up-Firing WOWCAST WOW Orchestra WOW Interface AI Room Calibration Pro AI Sound Pro Apple AirPlay Amazon Alexa Google Home Spotify TIDAL Connect Google Cast LG ThinQ HDMI eARC Bluetooth 24-bit Hi-Res Audio Saudi Arabia KSA Official LG'
    }
}

def js_str(s):
    if s is None: return '""'
    s = str(s).replace('\\','\\\\').replace('"','\\"').replace('\n','\\n').replace('\r','')
    return f'"{s}"'

def fmt_product(p, ov):
    gal = p.get('gallery', [])
    mods = p.get('modules', [])
    specs = p.get('specs', [])
    # Flatten modules → feat
    feat = []
    for m in mods:
        title = m.get('head','').strip()
        desc = m.get('body','').strip()
        for img in m.get('imgs', []):
            feat.append({
                'a': img.get('a',''),
                'p': img.get('p',''),
                't': title[:120] if title else img.get('a','')[:80],
                'd': desc[:300] if desc else '',
                'w': img.get('w',0), 'h': img.get('h',0)
            })
    sp = {}
    for s in specs:
        k = re.sub(r'[^A-Za-z0-9_]', '_', s['k'])[:40]
        if k and k not in sp:
            sp[k] = s['v']
    pr = 'SAR ' + re.sub(r'\s+','',p.get('curPrice','').strip()) if p.get('curPrice','').strip() else ''
    op = 'SAR ' + re.sub(r'\s+','',p.get('origPrice','').strip()) if p.get('origPrice','').strip() else ''
    nm = ov.get('nm') or p.get('h1','').strip()
    gal_s = '[' + ','.join('{a:%s,p:%s,w:%d,h:%d}' % (js_str(g['a']),js_str(g['p']),g.get('w',0),g.get('h',0)) for g in gal) + ']'
    feat_s = '[' + ','.join('{a:%s,p:%s,t:%s,d:%s,w:%d,h:%d}' % (js_str(f['a']),js_str(f['p']),js_str(f['t']),js_str(f['d']),f.get('w',0),f.get('h',0)) for f in feat) + ']'
    sp_s = '{' + ','.join(f'{js_str(k)}:{js_str(v)}' for k,v in sp.items()) + '}'
    bul_s = '[' + ','.join(js_str(b) for b in ov['bul']) + ']'
    faq_s = '[' + ','.join([
        '{q:"What is the model code?",a:%s}' % js_str(p['id']),
        '{q:"Is this the official LG model sold in Saudi Arabia?",a:"Yes. Official LG product sold and serviced by LG Saudi Arabia authorised channels."}',
        '{q:"What is the warranty?",a:"10-year warranty on the Smart Inverter Compressor and full LG Saudi Arabia manufacturer warranty on the appliance."}',
    ]) + ']'
    promo_s = '[{icon:"Free Delivery",tip:"Free delivery across KSA"},{icon:"Free Installation",tip:"Free installation service"},{icon:"Easy Installment",tip:"Flexible installments via Tamara"},{icon:"Bank Offers",tip:"Extra savings with partner banks"},{icon:"5% Welcome Discount",tip:"5% off for LG Members"}]'
    disc_s = '["All images and specifications sourced from LG.com Saudi Arabia.","Features and availability may vary by region and model."]'
    return (
        '{id:%s,dv:%s,cat:%s,sub:%s,ico:%s,nm:%s,pr:%s,op:%s,url:%s,crawled:true,'
        'amz_title:%s,amz_desc:%s,'
        'gal:%s,feat:%s,sp:%s,tags:[],bul:%s,faq:%s,promo:%s,disc:%s,kw:%s}' % (
        js_str(p['id']), js_str(ov['dv']), js_str(ov['cat']), js_str(ov['sub']), js_str(ov['ico']),
        js_str(nm), js_str(pr), js_str(op), js_str(p.get('url','')),
        js_str(ov['amz_title']), js_str(ov['amz_desc']),
        gal_s, feat_s, sp_s, bul_s, faq_s, promo_s, disc_s, js_str(ov['kw'])
    ))

def parse_entries(body):
    """brace-depth split of P[] body into individual product literals."""
    entries=[]
    i,n=0,len(body)
    while i<n and body[i]!='{': i+=1
    while i<n:
        if body[i]!='{': i+=1; continue
        start=i; depth=0; in_str=False; qc=None
        j=i
        while j<n:
            c=body[j]
            if in_str:
                if c=='\\': j+=2; continue
                if c==qc: in_str=False
                j+=1; continue
            if c in ('"',"'"): in_str=True; qc=c; j+=1; continue
            if c=='{': depth+=1
            elif c=='}':
                depth-=1
                if depth==0:
                    entries.append(body[start:j+1]); i=j+1; break
            j+=1
        else: break
    return entries

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('pid')
    args=ap.parse_args()
    pid=args.pid
    if pid not in OVERRIDES:
        print(f'[ERR] no override for {pid}'); return
    # Load crawl
    crawl_path=f'{BASE}/crawl_v2/{pid}.json'
    with open(crawl_path, encoding='utf-8') as f:
        p=json.load(f)
    ov=OVERRIDES[pid]
    # Load v6_18
    with open(V6_18, encoding='utf-8') as f:
        html=f.read()
    # Backup
    bak=V6_18.replace('.html', f'.pre_{pid}.html')
    with open(bak,'w',encoding='utf-8') as f: f.write(html)
    print(f'backup: {bak}')
    # Parse P[]
    m=re.search(r'(const P=\[)(.*?)(\n\];)', html, re.DOTALL)
    if not m: print('[ERR] P[] not found'); return
    p_hdr,p_body,p_ftr=m.group(1),m.group(2),m.group(3)
    entries=parse_entries(p_body)
    # Remove any existing entry with same id
    kept=[e for e in entries if not re.match(rf'\{{id:"{re.escape(pid)}"', e)]
    # Build new entry
    new_entry=fmt_product(p, ov)
    # Insert at top
    all_entries=[new_entry]+kept
    new_body='\n'+',\n'.join(all_entries)+','
    new_html=html[:m.start()]+p_hdr+new_body+p_ftr+html[m.end():]
    with open(V6_18,'w',encoding='utf-8') as f: f.write(new_html)
    print(f'Injected {pid} at TOP. Total P entries: {len(all_entries)}')
    # Stats
    print(f'  H1: {p["h1"]}')
    print(f'  Price: SAR {p.get("curPrice","")} (orig: SAR {p.get("origPrice","")})')
    print(f'  Gallery: {len(p.get("gallery",[]))} images (first: {p["gallery"][0]["a"][:60] if p.get("gallery") else "-"})')
    print(f'  Modules: {len(p.get("modules",[]))}')
    print(f'  Specs: {len(p.get("specs",[]))}')
    print(f'  Title({len(ov["amz_title"])}c): {ov["amz_title"]}')
    print(f'  Bullets: {len(ov["bul"])}')

if __name__=='__main__':
    main()
