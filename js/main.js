document.addEventListener('DOMContentLoaded', () => {
    // DOM 요소 참조
    const jasoForm = document.getElementById('jaso-form');
    const jobInput = document.getElementById('job');
    const expInput = document.getElementById('experience');
    const strInput = document.getElementById('strength');
    const submitBtn = document.getElementById('submit-btn');
    
    const loadingEl = document.getElementById('loading');
    const loadingText = document.getElementById('loading-text');
    const errorEl = document.getElementById('error-message');
    
    const resultSection = document.getElementById('result-section');
    const resultText = document.getElementById('result-text');
    const resultCharCount = document.getElementById('result-char-count');
    const copyBtn = document.getElementById('copy-btn');

    const expCount = document.getElementById('exp-count');
    const strCount = document.getElementById('str-count');

    // 1. 실시간 글자 수 카운터
    function updateCharCount(inputEl, displayEl) {
        if (!inputEl || !displayEl) return;
        displayEl.textContent = inputEl.value.length;
    }

    expInput.addEventListener('input', () => updateCharCount(expInput, expCount));
    strInput.addEventListener('input', () => updateCharCount(strInput, strCount));

    // 2. 프리셋 예시 데이터
    const presets = {
        dev: {
            job: '프론트엔드 개발자',
            experience: '3개월간 4인 팀으로 e-커머스 웹 프로젝트를 진행하며 장바구니 및 결제 페이지 UI를 구현했습니다. Lighthouse 성능 측정을 통해 이미지 최적화 및 렌더링 속도를 35% 개선한 경험이 있습니다.',
            strength: '신규 프레임워크와 기술 습득 속도가 빠르며, 기획자 및 디자이너와의 커뮤니케이션을 통해 사용자 중심의 직관적인 인터페이스를 구현하는 집념이 있습니다.'
        },
        marketing: {
            job: '콘텐츠 마케터',
            experience: '스타트업 서포터즈로 활동하며 인스타그램 카드뉴스 20편을 자체 기획·제작했습니다. 타겟 오디언스 분석을 통해 팔로워 수를 전월 대비 140% 성장시켰습니다.',
            strength: '트렌드를 빠르게 포착하여 대중 친화적인 스토리텔링으로 전환하는 감각과, 데이터(CTR, 도달률) 기반으로 콘텐츠를 개선하는 분석적 사고력을 갖추었습니다.'
        },
        business: {
            job: '서비스 기획 및 사업개발',
            experience: '교내 창업 동아리에서 대학생 중고 전자기기 거래 매칭 서비스를 기획하고 100명의 학생을 대상으로 설문 및 심층 인터뷰를 진행하여 MVP 핵심 기능 3가지를 도출했습니다.',
            strength: '고객의 숨겨진 니즈를 파악하는 경청 능력과, 다양한 이해관계자를 설득하고 프로젝트 일정을 철저히 조율하는 협업 리더십이 강점입니다.'
        }
    };

    document.querySelectorAll('.btn-preset').forEach(btn => {
        btn.addEventListener('click', () => {
            const presetKey = btn.dataset.preset;
            if (presets[presetKey]) {
                jobInput.value = presets[presetKey].job;
                expInput.value = presets[presetKey].experience;
                strInput.value = presets[presetKey].strength;
                updateCharCount(expInput, expCount);
                updateCharCount(strInput, strCount);
                hideError();
                jobInput.focus();
            }
        });
    });

    // 3. 자소서 문장 생성 폼 제출
    jasoForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const job = jobInput.value.trim();
        const experience = expInput.value.trim();
        const strength = strInput.value.trim();

        // [실패 처리 1] 빈 입력 (필수값 누락) 검증
        if (!job || !experience || !strength) {
            showError('⚠️ 지원 직무, 주요 경험, 핵심 강점을 모두 입력해주세요.');
            return;
        }

        // UI 상태 초기화 (로딩 시작)
        hideError();
        resultSection.classList.add('hidden');
        loadingEl.classList.remove('hidden');
        loadingText.textContent = 'AI가 자기소개서 문장을 작성하고 있습니다...';
        submitBtn.disabled = true;

        // 지연 시 안내 문구 타이머 (5초 경과 시 문구 변경)
        const delayTimer = setTimeout(() => {
            loadingText.textContent = '💡 Gemini 1.5가 문맥과 두괄식 구조를 정교하게 다듬고 있습니다. 잠시만 더 기다려주세요...';
        }, 4500);

        // [실패 처리 2] 지연/타임아웃 제어 (25초 타임아웃)
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 25000);

        try {
            const response = await fetch('/api/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ job, experience, strength }),
                signal: controller.signal
            });

            clearTimeout(delayTimer);
            clearTimeout(timeoutId);

            const data = await response.json().catch(() => ({}));

            // [실패 처리 3] API 오류 (4xx / 5xx)
            if (!response.ok) {
                const errorMsg = data.error || `서버 오류가 발생했습니다. (상태 코드: ${response.status})`;
                throw new Error(errorMsg);
            }

            if (!data.result) {
                throw new Error('생성된 결과 문장이 비어있습니다. 입력을 보완하여 다시 시도해주세요.');
            }

            // 성공: 결과 표시
            resultText.textContent = data.result;
            resultCharCount.textContent = `(공백 포함 약 ${data.result.length}자)`;
            resultSection.classList.remove('hidden');
            resultSection.scrollIntoView({ behavior: 'smooth', block: 'nearest' });

        } catch (error) {
            clearTimeout(delayTimer);
            clearTimeout(timeoutId);

            console.error('API 요청 실패:', error);

            if (error.name === 'AbortError') {
                showError('⏳ 서버 응답 시간이 초과되었습니다 (25초). 네트워크 연결 상태를 확인하시거나 잠시 후 다시 시도해주세요.');
            } else if (window.location.protocol === 'file:') {
                showError('⚠️ index.html 파일을 직접 열면 백엔드 API 및 .env 파일을 읽을 수 없습니다. 프로젝트 폴더의 start_local.bat를 더블 클릭하거나 python server.py 로 로컬 서버를 실행해주세요!');
            } else if (error instanceof TypeError && (error.message.includes('fetch') || error.message.includes('Failed'))) {
                showError('⚠️ 백엔드 서버에 연결할 수 없습니다. 로컬 서버(start_local.bat 또는 python server.py)가 켜져 있는지 확인해주세요.');
            } else {
                showError(`❌ 문장 생성 실패: ${error.message || '서버와의 통신에 실패했습니다.'}`);
            }
        } finally {
            loadingEl.classList.add('hidden');
            submitBtn.disabled = false;
        }
    });

    // 4. 원클릭 클립보드 복사
    copyBtn.addEventListener('click', async () => {
        const textToCopy = resultText.textContent;
        if (!textToCopy) return;

        try {
            await navigator.clipboard.writeText(textToCopy);
            const originalText = copyBtn.textContent;
            copyBtn.textContent = '✅ 복사 완료!';
            copyBtn.style.backgroundColor = '#dcfce7';
            setTimeout(() => {
                copyBtn.textContent = originalText;
                copyBtn.style.backgroundColor = '';
            }, 2000);
        } catch (err) {
            console.error('클립보드 복사 실패:', err);
            // 대체 복사 방식 (execCommand fallback)
            try {
                const tempTextArea = document.createElement('textarea');
                tempTextArea.value = textToCopy;
                document.body.appendChild(tempTextArea);
                tempTextArea.select();
                document.execCommand('copy');
                document.body.removeChild(tempTextArea);
                copyBtn.textContent = '✅ 복사 완료!';
                setTimeout(() => { copyBtn.textContent = '📋 복사하기'; }, 2000);
            } catch (fallbackErr) {
                alert('복사 권한이 차단되었습니다. 텍스트를 직접 드래그하여 복사해주세요.');
            }
        }
    });

    // 5. FAQ 아코디언 토글
    document.querySelectorAll('.faq-item').forEach(item => {
        const questionBtn = item.querySelector('.faq-question');
        questionBtn.addEventListener('click', () => {
            const isActive = item.classList.contains('active');
            // 다른 열린 아코디언 닫기
            document.querySelectorAll('.faq-item').forEach(other => other.classList.remove('active'));
            if (!isActive) {
                item.classList.add('active');
            }
        });
    });

    // 오류 표시 유틸리티
    function showError(msg) {
        errorEl.textContent = msg;
        errorEl.classList.remove('hidden');
        errorEl.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }

    function hideError() {
        errorEl.textContent = '';
        errorEl.classList.add('hidden');
    }
});
