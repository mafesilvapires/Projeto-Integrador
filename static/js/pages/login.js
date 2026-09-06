document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('form-verificacao');
    const pinInputs = Array.from(document.querySelectorAll('.campo-pin'));
    const tokenInput = document.getElementById('codigo') || document.getElementById('token-2fa');

    if (!form || pinInputs.length === 0) return;

    // Foco imediato no primeiro dígito
    pinInputs[0].focus();

    pinInputs.forEach((input, index) => {
        // Pular para o próximo ao digitar
        input.addEventListener('input', (e) => {
            const valor = input.value.replace(/\D/g, '');
            input.value = valor;

            if (valor && index < pinInputs.length - 1) {
                pinInputs[index + 1].focus();
            }
        });

        // Voltar para o anterior com Backspace
        input.addEventListener('keydown', (e) => {
            if (e.key === 'Backspace') {
                if (!input.value && index > 0) {
                    pinInputs[index - 1].focus();
                }
            } else if (e.key === 'ArrowLeft' && index > 0) {
                pinInputs[index - 1].focus();
            } else if (e.key === 'ArrowRight' && index < pinInputs.length - 1) {
                pinInputs[index + 1].focus();
            }
        });

        // Suporte para colar código completo (ex: 123456)
        input.addEventListener('paste', (e) => {
            e.preventDefault();
            const colar = (e.clipboardData || window.clipboardData).getData('text').replace(/\D/g, '');
            
            if (colar.length > 0) {
                colar.split('').slice(0, pinInputs.length).forEach((num, idx) => {
                    pinInputs[idx].value = num;
                });
                
                const proximoIndice = Math.min(colar.length, pinInputs.length - 1);
                pinInputs[proximoIndice].focus();
            }
        });
    });

    // Concatena os valores antes do envio
    form.addEventListener('submit', (e) => {
        const pinCompleto = pinInputs.map(input => input.value).join('');
        
        if (tokenInput) {
            tokenInput.value = pinCompleto;
        }

        if (pinCompleto.length !== pinInputs.length) {
            e.preventDefault();
            if (window.Swal) {
                Swal.fire({
                    text: `Por favor, preencha os ${pinInputs.length} dígitos do código.`,
                    confirmButtonColor: '#0070f3',
                    confirmButtonText: 'OK'
                });
            } else {
                alert(`Por favor, preencha os ${pinInputs.length} dígitos do código.`);
            }
        }
    });
});