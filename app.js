(() => {
  'use strict';
  const $ = (sel, base = document) => base.querySelector(sel);
  const $$ = (sel, base = document) => [...base.querySelectorAll(sel)];
  const form = $('#assessment-form');
  const steps = $$('.form-step');
  const nextBtn = $('#next-step');
  const backBtn = $('#prev-step');
  const submitBtn = $('#submit-form');
  const message = $('#form-message');
  const fileInput = $('#documents');
  const fileList = $('#file-list');
  const consultInput = $('#wants-consultation');
  const consultFields = $('#consultation-fields');
  const menu = $('.menu-toggle');
  const nav = $('#primary-nav');
  const toast = $('#toast');
  let currentStep = 1;
  let ready = false;
  let whatsappNumber = '';
  let toastHandle;
  const formatStep = ['','١ من ٤','٢ من ٤','٣ من ٤','٤ من ٤'];

  $('#current-year').textContent = new Date().getFullYear();
  menu?.addEventListener('click', () => {
    const open = nav.classList.toggle('open');
    menu.setAttribute('aria-expanded', String(open));
    menu.setAttribute('aria-label', open ? 'إغلاق القائمة' : 'فتح القائمة');
  });
  $$('#primary-nav a').forEach(a => a.addEventListener('click', () => {
    nav.classList.remove('open');
    menu?.setAttribute('aria-expanded', 'false');
  }));

  function showToast(text) {
    toast.textContent = text;
    toast.classList.add('show');
    clearTimeout(toastHandle);
    toastHandle = setTimeout(() => toast.classList.remove('show'), 5800);
  }
  function showError(text, success = false) {
    message.textContent = text;
    message.classList.add('visible');
    message.classList.toggle('success', success);
  }
  function clearError() {
    message.textContent = '';
    message.className = 'form-message';
  }
  function showStep(n) {
    currentStep = n;
    steps.forEach((el, i) => el.classList.toggle('active', i === n-1));
    $('#form-counter').textContent = formatStep[n];
    $('#progress-fill').style.width = `${n*25}%`;
    nextBtn.classList.toggle('hidden', n === 4);
    backBtn.classList.toggle('hidden', n === 1);
    submitBtn.classList.toggle('hidden', n !== 4);
    clearError();
    if (n === 4) fillReview();
    $('.form-card').scrollIntoView({behavior: 'smooth', block:'start'});
  }
  function fieldIsValid(el) {
    if (el.type === 'file') return true;
    el.classList.remove('invalid');
    if (!el.checkValidity()) {el.classList.add('invalid');return false;}
    if (el.name === 'phone' && el.value.replace(/\D/g,'').length < 9) {el.classList.add('invalid');return false;}
    return true;
  }
  function validateStep(n) {
    const active = steps[n-1];
    const fields = $$('input[required],select[required],textarea[required]', active).filter(el => !el.disabled);
    let firstInvalid;
    for (const el of fields) if (!fieldIsValid(el) && !firstInvalid) firstInvalid = el;
    if (firstInvalid) {
      showError(firstInvalid.type === 'checkbox' ? 'لازم توافق على إشعار الخصوصية قبل الإرسال.' : 'راجع الحقول المطلوبة (*) وتأكد من صحة بيانات التواصل.');
      firstInvalid.focus();
      return false;
    }
    if (n === 3) return validateFiles(true);
    if (n === 4 && consultInput.checked) {
      const date = $('#preferred-date');
      const slot = $('[name="preferred_slot"]');
      if (!date.value || !slot.value || date.value < date.min) {
        showError('اختار اليوم والفترة المناسبة للاستشارة، أو ألغِ طلب الموعد.');
        (!date.value || date.value < date.min ? date : slot).focus();
        return false;
      }
    }
    return true;
  }
  function validateFiles(show = false) {
    const files = [...fileInput.files];
    const allowed = /\.(pdf|jpe?g|png)$/i;
    const total = files.reduce((sum,f) => sum + f.size, 0);
    let error = '';
    if (files.length > 3) error = 'مسموح برفع 3 ملفات فقط.';
    else if (files.some(f => !allowed.test(f.name) || !['application/pdf','image/jpeg','image/png',''].includes(f.type))) error = 'نوع الملفات لازم يكون PDF أو JPG أو PNG.';
    else if (files.some(f => f.size > 5*1024*1024)) error = 'كل ملف لازم يكون أقل من 5 MB.';
    else if (total > 10*1024*1024) error = 'إجمالي حجم الملفات لازم يكون أقل من 10 MB.';
    if (error && show) showError(error);
    return !error;
  }
  nextBtn.addEventListener('click', () => {if (validateStep(currentStep)) showStep(currentStep + 1);});
  backBtn.addEventListener('click', () => showStep(currentStep - 1));
  $$('input,select,textarea', form).forEach(el => {
    el.addEventListener('input', () => el.classList.remove('invalid'));
    el.addEventListener('change', () => el.classList.remove('invalid'));
  });
  fileInput.addEventListener('change', () => {
    fileList.replaceChildren();
    const files = [...fileInput.files];
    for (const file of files) {
      const chip = document.createElement('span');
      chip.textContent = `${file.name} (${(file.size/1024/1024).toFixed(1)} MB)`;
      fileList.appendChild(chip);
    }
    if (!validateFiles(true)) fileInput.value = '';
    if (fileInput.files.length === 0) fileList.replaceChildren();
  });
  consultInput.addEventListener('change', () => consultFields.classList.toggle('hidden', !consultInput.checked));
  const tomorrow = new Date();
  tomorrow.setDate(tomorrow.getDate() + 1);
  $('#preferred-date').min = `${tomorrow.getFullYear()}-${String(tomorrow.getMonth()+1).padStart(2,'0')}-${String(tomorrow.getDate()).padStart(2,'0')}`;

  const field = name => form.elements.namedItem(name)?.value?.trim() || '';
  function fillReview() {
    const review = $('#review-card');
    review.replaceChildren();
    const items = [
      ['الاسم',field('full_name')],['المرحلة',({'Bachelor':'بكالوريوس','Master':'ماجستير'})[field('degree')]||'—'],
      ['الدولة',({'Germany':'ألمانيا','Austria':'النمسا','Both':'البلدين'})[field('destination')]||'—'],
      ['التخصص المطلوب',field('target_major')],
      ['لغة الدراسة',({'English':'الإنجليزية','German':'الألمانية','Both':'اللغتين'})[field('study_language')]||'—'],
      ['المستندات',`${fileInput.files.length} ملف`]
    ];
    items.forEach(([label, value]) => {
      const row = document.createElement('div');row.className='review-row';
      const title = document.createElement('span');title.textContent=label;
      const val = document.createElement('strong');val.textContent=value;
      row.append(title,val);review.appendChild(row);
    });
  }
  $$('.whatsapp-action').forEach(btn => btn.addEventListener('click', () => {
    if (whatsappNumber) {
      const text = encodeURIComponent('أهلاً، عايز أعرف تفاصيل خدمة التقييم والتقديم للجامعات في ألمانيا والنمسا.');
      window.open(`https://wa.me/${whatsappNumber}?text=${text}`, '_blank', 'noopener,noreferrer');
    } else showToast('رقم واتساب العمل لسه ما اتضافش. ده نموذج تجريبي، وهيتفعّل عند تجهيز بيانات التواصل.');
  }));

  async function loadConfig() {
    try {
      const res = await fetch('/api/config', {cache:'no-store'});
      if (!res.ok) return;
      const config = await res.json();
      ready = Boolean(config.form_enabled);
      whatsappNumber = config.whatsapp_number || '';
      if (ready) $('#demo-note').classList.add('hidden');
    } catch (_) { /* Local file preview: no backend available. */ }
  }
  loadConfig();

  form.addEventListener('submit', async e => {
    e.preventDefault();
    if (!validateStep(4) || !validateFiles(true)) return;
    if (!ready) {
      showError('النسخة دي للمعاينة فقط؛ البيانات والملفات لم يتم إرسالها. لتفعيل الإرسال لازم نجهز بريد الاستقبال وسياسة الخصوصية القانونية.');
      return;
    }
    const data = new FormData(form);
    if (!consultInput.checked) {
      data.delete('preferred_date');data.delete('preferred_slot');
    }
    submitBtn.disabled = true;
    submitBtn.textContent = 'جاري الإرسال...';
    clearError();
    try {
      const res = await fetch('/api/assessment', {method:'POST',body:data,headers:{'Accept':'application/json'}});
      const response = await res.json().catch(()=>({}));
      if (!res.ok) throw Error(response.detail || 'تعذر إرسال الطلب. جرب مرة تانية.');
      form.reset();fileList.replaceChildren();consultFields.classList.add('hidden');
      showStep(1);
      showError('تم إرسال طلبك ومستنداتك بنجاح. هنراجع المعلومات ونتواصل معاك. طلب الموعد — لو اخترته — لسه محتاج تأكيد.',true);
      $('.form-card').scrollIntoView({behavior:'smooth',block:'start'});
    } catch (error) {
      showError(typeof error.message==='string'?error.message:'حصل خطأ أثناء الإرسال. حاول مرة تانية.');
    } finally {
      submitBtn.disabled=false;submitBtn.innerHTML='إرسال طلب التقييم <span aria-hidden="true">←</span>';
    }
  });
})();
