import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import { AnalysisResult } from '../models/analysis.model';

@Injectable({ providedIn: 'root' })
export class AnalysisService {
  private readonly api = environment.apiUrl;

  constructor(private http: HttpClient) {}

  /** Retorna análise técnica + recomendação DQN para uma ação */
  getAnalysis(ticker: string): Observable<AnalysisResult> {
    return this.http.get<AnalysisResult>(`${this.api}/analysis/${ticker}`);
  }

  /** Retorna histórico de análises de uma ação */
  getAnalysisHistory(ticker: string, limit = 30): Observable<any[]> {
    return this.http.get<any[]>(`${this.api}/analysis/${ticker}/history?limit=${limit}`);
  }
}
