import { Component, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './tela-inicial.html',
  styleUrls: ['./tela-inicial.css']
})
export class LoginComponent {
  loginForm: FormGroup;
  showPassword = signal(false);

  constructor(private fb: FormBuilder) {
    this.loginForm = this.fb.group({
      email: ['', [Validators.required, Validators.email]],
      password: ['', [Validators.required, Validators.minLength(6)]],
      rememberMe: [true]
    });
  }

  togglePasswordVisibility(): void {
    this.showPassword.update(value => !value);
  }

  onSubmit(): void {
    if (this.loginForm.valid) {
      console.log('Dados de acesso:', this.loginForm.value);
      // Implementar chamada ao serviço de autenticação aqui
    } else {
      this.loginForm.markAllAsTouched();
    }
  }

  onGoogleLogin(): void {
    console.log('Iniciar autenticação via Google Workspace');
    // Implementar fluxo OAuth Google aqui
  }
}
export class TelaInicial {}
