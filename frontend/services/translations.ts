import { Language } from '@/types/agent'
import { useCustomerStore } from '@/store/useCustomerStore'

type TranslationMap = Record<string, Record<Language, string>>

const translations: TranslationMap = {
  'Dashboard': { hi: 'डैशबोर्ड', bn: 'ড্যাশবোর্ড', ta: 'டாஷ்போர்டு', en: 'Dashboard' },
  'Voice Banking': { hi: 'वॉइस बैंकिंग', bn: 'ভয়েস ব্যাংকিং', ta: 'குரல் வங்கி', en: 'Voice Banking' },
  'Onboarding': { hi: 'पंजीकरण', bn: 'নিবন্ধন', ta: 'பதிவு', en: 'Onboarding' },
  'Audit Trail': { hi: 'ऑडिट ट्रेल', bn: 'অডিট ট্রেইল', ta: 'தணிக்கை தடம்', en: 'Audit Trail' },
  'Consent': { hi: 'सहमति', bn: 'সম্মতি', ta: 'ஒப்புதல்', en: 'Consent' },
  'Settings': { hi: 'सेटिंग्स', bn: 'সেটিংস', ta: 'அமைப்புகள்', en: 'Settings' },
  'Balance': { hi: 'शेष राशि', bn: 'জমা অর্থ', ta: 'இருப்பு', en: 'Balance' },
  'Active Products': { hi: 'सक्रिय उत्पाद', bn: 'সক্রিয় পণ্য', ta: 'செயலில் உள்ள தயாரிப்புகள்', en: 'Active Products' },
  'Pending Actions': { hi: 'लंबित कार्रवाइयाँ', bn: 'অপেক্ষামান কাজ', ta: 'நிலுவை நடவடிக்கைகள்', en: 'Pending Actions' },
  'Last Activity': { hi: 'पिछली गतिविधि', bn: 'শেষ কার্যকলাপ', ta: 'கடைசி செயல்பாடு', en: 'Last Activity' },
  'Recent Agent Activity': { hi: 'हाल की एजेंट गतिविधि', bn: 'সাম্প্রতিক এজেন্ট কার্যকলাপ', ta: 'சமீபத்திய முகவர் செயல்பாடு', en: 'Recent Agent Activity' },
  'Recommendations': { hi: 'सुझाव', bn: 'প্রস্তাবনা', ta: 'பரிந்துரைகள்', en: 'Recommendations' },
  'Ask Saarthi': { hi: 'सारथी से पूछें', bn: 'সারথিকে জিজ্ঞাসা করুন', ta: 'சார்த்தியிடம் கேளுங்கள்', en: 'Ask Saarthi' },
  'Your Consent, Your Control': { hi: 'आपकी सहमति, आपका नियंत्रण', bn: 'আপনার সম্মতি, আপনার নিয়ন্ত্রণ', ta: 'உங்கள் ஒப்புதல், உங்கள் கட்டுப்பாடு', en: 'Your Consent, Your Control' },
  'Every AI action is logged and auditable.': { hi: 'हर AI कार्रवाई लॉग और ऑडिट योग्य है।', bn: 'প্রতিটি AI ক্রিয়া লগ এবং অডিটযোগ্য।', ta: 'ஒவ்வொரு AI செயலும் பதிவு செய்யப்பட்டு தணிக்கை செய்யக்கூடியது.', en: 'Every AI action is logged and auditable.' },
  'Language Preferences': { hi: 'भाषा प्राथमिकताएँ', bn: 'ভাষা পছন্দ', ta: 'மொழி விருப்பத்தேர்வுகள்', en: 'Language Preferences' },
  'Notification Preferences': { hi: 'सूचना प्राथमिकताएँ', bn: 'বিজ্ঞপ্তি পছন্দ', ta: 'அறிவிப்பு விருப்பத்தேர்வுகள்', en: 'Notification Preferences' },
  'Data & Privacy': { hi: 'डेटा और गोपनीयता', bn: 'ডেটা এবং গোপনীয়তা', ta: 'தரவு மற்றும் தனியுரிமை', en: 'Data & Privacy' },
  'Clear my conversation memory': { hi: 'मेरी वार्तालाप मेमोरी साफ़ करें', bn: 'আমার কথোপকথন মেমরি সাফ করুন', ta: 'என் உரையாடல் நினைவகத்தை அழிக்கவும்', en: 'Clear my conversation memory' },
  'Language': { hi: 'भाषा', bn: 'ভাষা', ta: 'மொழி', en: 'Language' },
  'Voice KYC': { hi: 'आवाज़ KYC', bn: 'ভয়েস KYC', ta: 'குரல் KYC', en: 'Voice KYC' },
  'Documents': { hi: 'दस्तावेज़', bn: 'নথিপত্র', ta: 'ஆவணங்கள்', en: 'Documents' },
  'Account Type': { hi: 'खाता प्रकार', bn: 'অ্যাকাউন্টের ধরন', ta: 'கணக்கு வகை', en: 'Account Type' },
  'Please say your name and village': { hi: 'कृपया अपना नाम और गाँव बोलें', bn: 'অনুগ্রহ করে আপনার নাম এবং গ্রাম বলুন', ta: 'உங்கள் பெயர் மற்றும் கிராமத்தைச் சொல்லுங்கள்', en: 'Please say your name and village' },
  'Upload your documents': { hi: 'अपने दस्तावेज़ अपलोड करें', bn: 'আপনার নথি আপলোড করুন', ta: 'உங்கள் ஆவணங்களைப் பதிவேற்றவும்', en: 'Upload your documents' },
  'Select Account Type': { hi: 'खाता प्रकार चुनें', bn: 'অ্যাকাউন্টের ধরন নির্বাচন করুন', ta: 'கணக்கு வகையைத் தேர்ந்தெடுக்கவும்', en: 'Select Account Type' },
  'Transaction History': { hi: 'लेन-देन का इतिहास', bn: 'লেনদেনের ইতিহাস', ta: 'பரிவர்த்தனை வரலாறு', en: 'Transaction History' },
  'Profile': { hi: 'प्रोफ़ाइल', bn: 'প্রোফাইল', ta: 'சுயவிவரம்', en: 'Profile' },
  'Action Preview': { hi: 'कार्रवाई पूर्वावलोकन', bn: 'কর্ম পূর্বদর্শন', ta: 'செயல் முன்னோட்டம்', en: 'Action Preview' },
  'Consent Manager': { hi: 'सहमति प्रबंधक', bn: 'সম্মতি ব্যবস্থাপক', ta: 'ஒப்புதல் மேலாளர்', en: 'Consent Manager' },
  'No pending action': { hi: 'कोई लंबित कार्रवाई नहीं', bn: 'কোনো অপেক্ষামান কাজ নেই', ta: 'நிலுவை நடவடிக்கை எதுவும் இல்லை', en: 'No pending action' },
  'No consent records yet': { hi: 'अभी तक कोई सहमति रिकॉर्ड नहीं', bn: 'এখনো কোনো সম্মতি রেকর্ড নেই', ta: 'இன்னும் ஒப்புதல் பதிவுகள் எதுவும் இல்லை', en: 'No consent records yet' },
  'No audit entries found': { hi: 'कोई ऑडिट प्रविष्टि नहीं मिली', bn: 'কোনো অডিট এন্ট্রি পাওয়া যায়নি', ta: 'தணிக்கை உள்ளீடுகள் எதுவும் காணப்படவில்லை', en: 'No audit entries found' },
  '+1 this month': { hi: 'इस महीने +1', bn: 'এই মাসে +1', ta: 'இந்த மாதம் +1', en: '+1 this month' },
  'Idle balance FD': { hi: 'निष्क्रिय शेष FD', bn: 'নিষ্ক্রিয় ব্যালেন্স FD', ta: 'செயலற்ற இருப்பு FD', en: 'Idle balance FD' },
}

export function t(key: string): string {
  const lang = useCustomerStore.getState()?.customer?.language || 'en'
  return translations[key]?.[lang] || key
}

export function useT() {
  const lang = useCustomerStore((s) => s.customer?.language || 'en')
  return (key: string) => translations[key]?.[lang] || key
}
