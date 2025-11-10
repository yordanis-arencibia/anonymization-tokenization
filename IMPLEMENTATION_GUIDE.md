## Production Implementation Guide: Integrating Presidio with NestJS and OpenAI

This is an excellent architecture for building a responsible and secure AI agent. Integrating Microsoft Presidio is a crucial step for protecting user privacy (PII) before data reaches OpenAI or is stored in your database.

The key here is that Presidio is a Python library. Since you are in a NestJS (Node.js/TypeScript) environment, the most robust and recommended solution is not to run Python directly from Node, but to treat Presidio as a separate microservice.

### 💡 Key Concept: Presidio as a Microservice

Your architecture will look like this:

1. **User sends a message.**
2. **NestJS (Your Agent)** receives the message.
3. **NestJS sends** the message text to a **Presidio Microservice (Python)** that you will create.
4. **Presidio Service** analyzes, identifies, and anonymizes PII (e.g., "John Doe" -> "<PERSON>").
5. **Presidio Service** returns the anonymized text to NestJS.
6. **NestJS** now has two versions: the original text and the anonymized text. 
7. It saves the **anonymized text** (or as you decide to handle it) to **PostgreSQL**.
8. **NestJS** saves the AI response to PostgreSQL and returns it to the user.
9. The agent sends the **anonymized text** to the **OpenAI API**.
10. **OpenAI** responds to the anonymized text.

### 📋 Steps for Integration

Here are the practical steps to build this.

#### Step 1: Create the Presidio Microservice (Python)

You will need a simple service, using FastAPI or Flask, that exposes an endpoint to anonymize text.

**Python Dependencies (in a requirements.txt):**
```text
fastapi
uvicorn
presidio-analyzer
presidio-anonymizer
spacy
en_core_web_lg  # Spacy model for English
```

**Spacy Model Installation:**
```bash
python -m spacy download en_core_web_lg
```

> **Note:** This guide uses the English language model `en_core_web_lg`. If you need to process other languages, you can download the appropriate spaCy model (e.g., `es_core_news_lg` for Spanish, `fr_core_news_lg` for French, etc.).

**Microservice Code Example (main.py with FastAPI):**

```python
from fastapi import FastAPI
from pydantic import BaseModel
from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig

# Configuration for English
analyzer = AnalyzerEngine(supported_languages=["en"])
anonymizer = AnonymizerEngine()

app = FastAPI()

class TextIn(BaseModel):
    text: str

class AnonymizedOut(BaseModel):
    text: str

@app.post("/anonymize", response_model=AnonymizedOut)
async def anonymize_text(item: TextIn):
    try:
        # 1. Analyze the text for PII
        # We explicitly use 'en' for English language processing
        analyzer_results = analyzer.analyze(text=item.text, language="en")
        
        # 2. Anonymize the text
        # We use <ENTITY> as a placeholder (e.g., <PERSON>, <PHONE_NUMBER>)
        anonymized_result = anonymizer.anonymize(
            text=item.text,
            analyzer_results=analyzer_results,
            operators={"DEFAULT": OperatorConfig("replace", {"new_value": "<ENTITY>"})}
        )
        
        return AnonymizedOut(text=anonymized_result.text)

    except Exception as e:
        # Error handling
        return AnonymizedOut(text=item.text) # Return original if it fails

# To run: uvicorn main:app --host 0.0.0.0 --port 8001
```

#### Step 2: Create a Presidio Service in NestJS

In your NestJS project, create a new service responsible for communicating with the Python microservice.

**First, install the NestJS HTTP module:**
```bash
npm install @nestjs/axios axios
```

**presidio.service.ts:**
```typescript
import { Injectable } from '@nestjs/common';
import { HttpService } from '@nestjs/axios';
import { firstValueFrom } from 'rxjs';

@Injectable()
export class PresidioService {
  // Make sure this URL is in your environment variables
  private presidioApiUrl = 'http://localhost:8001/anonymize';

  constructor(private readonly httpService: HttpService) {}

  /**
   * Sends text to the Presidio microservice for anonymization.
   * @param text The original user text.
   * @returns The anonymized text.
   */
  async anonymize(text: string): Promise<string> {
    try {
      const response = await firstValueFrom(
        this.httpService.post<{ text: string }>(this.presidioApiUrl, { text }),
      );
      return response.data.text;
    } catch (error) {
      console.error('Error contacting Presidio service:', error);
      // Fallback: if Presidio fails, return the original text
      // WARNING! This would send PII. Decide your failure policy.
      // You might want to return an error to the user instead.
      return text;
    }
  }
}
```

> Don't forget to import `HttpModule` in your `AppModule` or in the module where your chat services reside.

#### Step 3: Integrate into your Chat Flow (OpenAI and PostgreSQL)

Now, in your main chat service (e.g., `chat.service.ts`), you will use the `PresidioService` before calling OpenAI and your database.

```typescript
import { Injectable } from '@nestjs/common';
import { OpenaiService } from './openai.service'; // Your OpenAI service
import { PresidioService } from './presidio.service'; // Our new service
import { PrismaService } from './prisma.service'; // Or your TypeORM repository, etc.

@Injectable()
export class ChatService {
  constructor(
    private readonly openaiService: OpenaiService,
    private readonly presidioService: PresidioService,
    private readonly db: PrismaService, // Assuming Prisma for PostgreSQL
  ) {}

  async handleUserMessage(userId: string, originalMessage: string) {
    // 1. ANONYMIZE
    // Send the original message to Presidio
    const anonymizedMessage = await this.presidioService.anonymize(
      originalMessage,
    );

    // 2. CALL OPENAI
    // Use the *anonymized* message for the API call
    const aiResponse = await this.openaiService.getChatCompletion(
      anonymizedMessage,
      // ...you can include chat history (also anonymized)
    );

    // 3. SAVE TO POSTGRESQL
    // Important decision! What do you save?
    await this.db.chatMessage.create({
      data: {
        userId: userId,
        
        // OPTION A (Safest): Never save the PII
        userMessage: anonymizedMessage, 
        
        // OPTION B (Less safe): Save both, if legally necessary
        // userMessageOriginal: originalMessage, // Risky!
        // userMessageAnonymized: anonymizedMessage,
        
        aiResponse: aiResponse,
      },
    });

    // 4. RESPOND TO USER
    return aiResponse;
  }
}
```

### 💾 Considerations for PostgreSQL

The most important part of your question is how to handle the chat history in PostgreSQL.

**The Safest Practice:** Save only the anonymized text (`anonymizedMessage`). If you don't have the PII, it can't be stolen. The context for the AI remains intact (e.g., "I need help with my order, my name is <PERSON>").

**If You Must Store PII:** If your business logic requires the original PII (e.g., to process an order), do not store it in the same chat table. Store it in a separate, highly secure table with column-level encryption (using `pgcrypto`, for example) and very strict access policies. The general chat history should remain anonymized.

**Chat History:** When you pass the chat history to OpenAI in subsequent turns, ensure that all the history you retrieve from PostgreSQL is already anonymized.

### 🌎 Important: Language Configuration

Presidio's success depends on it understanding the language.

**Spacy Model:** As you saw in the Python example, we used `en_core_web_lg` for English language processing. It is essential that the Presidio microservice downloads and uses the correct language model. For other languages, you would need to switch to the appropriate model (e.g., `es_core_news_lg` for Spanish, `fr_core_news_lg` for French).

**Language Parameter:** When calling `analyzer.analyze(...)`, make sure to pass the correct language (e.g., `language="en"` for English, `language="es"` for Spanish, `language="fr"` for French) to force the use of the correct recognizers and improve PII detection accuracy.

---

*Would you like me to elaborate on the PostgreSQL encryption setup with pgcrypto or provide a more detailed example of how to manage the anonymized chat history?*

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [NestJS HTTP Module Documentation](https://docs.nestjs.com/techniques/http-module)