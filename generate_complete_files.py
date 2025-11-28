#!/usr/bin/env python3
"""
Generate complete updated files for Who Am I answer variants feature
Run this from /home/bbsisk/mathapp directory
"""
import os
import sys

def generate_admin_template():
    """Generate complete admin_who_am_i.html with answer variants support"""
    
    # Read original
    with open('templates/admin_who_am_i.html', 'r') as f:
        lines = f.readlines()
    
    output = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        
        # INSERT 1: After hint field in upload form (around line 327-329)
        if 'name="hint"' in line and i < 350 and 'edit_' not in line:
            output.append(line)
            # Skip to end of this div
            i += 1
            while i < len(lines) and '</div>' not in lines[i]:
                output.append(lines[i])
                i += 1
            output.append(lines[i])  # Add the </div>
            i += 1
            output.append(lines[i])  # Add the </div> for row
            
            # Now add new field
            output.append('''                    
                    <!-- NEW: Acceptable Answer Variants -->
                    <div class="mb-3">
                        <label class="form-label">
                            Acceptable Answer Variants
                            <i class="fas fa-info-circle text-muted" data-bs-toggle="tooltip" 
                               title="Enter all acceptable answers, one per line. Students can use any variant."></i>
                        </label>
                        <textarea class="form-control" name="accepted_answers" rows="4" 
                                  placeholder="Enter variants (one per line, or leave blank to auto-generate):
newton
isaac newton
sir isaac newton"></textarea>
                        <small class="text-muted">
                            💡 Leave blank to auto-generate common variants
                        </small>
                    </div>
                    <div class="row">
''')
            continue
        
        # INSERT 2: Replace edit form answer/hint fields (around line 382-390)
        if 'id="edit_answer"' in line:
            # Skip old fields
            while i < len(lines) and 'id="edit_hint"' not in lines[i]:
                i += 1
            # Skip hint field too
            while i < len(lines) and '</div>' not in lines[i]:
                i += 1
            i += 1  # Skip the </div>
            
            # Add new fields
            output.append('''                    <input type="hidden" id="edit_image_id">
                    
                    <div class="mb-3">
                        <label class="form-label">Primary Answer *</label>
                        <input type="text" class="form-control" id="edit_answer" required>
                        <small class="text-muted">Main answer displayed to students</small>
                    </div>
                    
                    <!-- NEW: Acceptable Answer Variants -->
                    <div class="mb-3">
                        <label class="form-label">
                            Acceptable Answer Variants
                            <button type="button" class="btn btn-sm btn-outline-primary ms-2" 
                                    onclick="autoGenerateVariants()">
                                <i class="fas fa-magic"></i> Auto-Generate
                            </button>
                        </label>
                        <textarea class="form-control" id="edit_accepted_answers" rows="5" 
                                  placeholder="Enter accepted variants, one per line"></textarea>
                        <small class="text-muted">
                            Students can answer with any of these (case-insensitive)
                        </small>
                    </div>
                    
                    <div class="mb-3">
                        <label class="form-label">Hint</label>
                        <input type="text" class="form-control" id="edit_hint">
                    </div>
''')
            continue
        
        # INSERT 3: Add variant count display in image cards (around line 235-240)
        if '<h6 class="card-title">{{ image.answer }}</h6>' in line:
            output.append(line)
            output.append('''                            
                            <!-- NEW: Show variants count -->
                            {% if image.accepted_answers_count %}
                            <small class="text-muted">
                                <i class="fas fa-list"></i> 
                                {{ image.accepted_answers_count }} accepted variants
                            </small>
                            {% endif %}
''')
            i += 1
            continue
        
        # INSERT 4: Update JavaScript - add before openEditModal function (around line 493)
        if 'function openEditModal(imageId)' in line:
            # Add new helper functions first
            output.append('''
// NEW: Auto-generate answer variants
function autoGenerateVariants() {
    const answer = document.getElementById('edit_answer').value.trim();
    if (!answer) {
        alert('Please enter a primary answer first');
        return;
    }
    const variants = generateAnswerVariants(answer);
    document.getElementById('edit_accepted_answers').value = variants.join('\\n');
}

function generateAnswerVariants(answer) {
    const variants = new Set();
    const answerLower = answer.toLowerCase().trim();
    variants.add(answerLower);
    
    // Remove titles
    const titles = ['dr.', 'dr', 'sir', 'professor', 'prof.', 'prof', 'dame', 'lord', 'lady'];
    for (const title of titles) {
        if (answerLower.startsWith(title + ' ')) {
            const withoutTitle = answerLower.replace(title + ' ', '').trim();
            variants.add(withoutTitle);
        }
    }
    
    // Name parts
    const parts = answerLower.split(/\\s+/);
    if (parts.length >= 2) {
        variants.add(parts[0]);  // First name
        variants.add(parts[parts.length - 1]);  // Last name
        if (parts.length > 2) {
            variants.add(`${parts[0]} ${parts[parts.length - 1]}`);
        }
        
        // Remove middle initials
        const filtered = parts.filter(p => p.length > 2 || !p.endsWith('.'));
        if (filtered.length !== parts.length) {
            variants.add(filtered.join(' '));
        }
    }
    
    // Remove punctuation
    const noPunct = answerLower.replace(/[.,\\/#!$%\\^&\\*;:{}=\\-_`~()]/g, '').trim();
    if (noPunct !== answerLower) {
        variants.add(noPunct);
    }
    
    return Array.from(variants).sort();
}

''')
            output.append(line)
            i += 1
            continue
        
        # REPLACE: Update openEditModal to use new GET endpoint and load accepted_answers
        if 'function openEditModal(imageId)' in line:
            output.append(line)
            # Skip old implementation
            bracket_count = 1
            i += 1
            while i < len(lines) and bracket_count > 0:
                if '{' in lines[i]:
                    bracket_count += lines[i].count('{')
                if '}' in lines[i]:
                    bracket_count -= lines[i].count('}')
                i += 1
            
            # Add new implementation
            output.append('''    fetch(`/admin/who-am-i/get/${imageId}`)
        .then(response => response.json())
        .then(data => {
            document.getElementById('edit_image_id').value = imageId;
            document.getElementById('edit_answer').value = data.answer;
            document.getElementById('edit_hint').value = data.hint || '';
            document.getElementById('edit_difficulty').value = data.difficulty;
            
            // NEW: Load accepted answers
            if (data.accepted_answers) {
                try {
                    const variants = JSON.parse(data.accepted_answers);
                    document.getElementById('edit_accepted_answers').value = variants.join('\\n');
                } catch(e) {
                    document.getElementById('edit_accepted_answers').value = '';
                }
            } else {
                document.getElementById('edit_accepted_answers').value = '';
            }
            
            // Populate topics checkboxes
            const topicsList = document.getElementById('edit_topics_list');
            topicsList.innerHTML = '';
            const allTopics = {{ all_topics|tojson }};
            allTopics.forEach(topic => {
                const label = document.createElement('label');
                const checkbox = document.createElement('input');
                checkbox.type = 'checkbox';
                checkbox.value = topic;
                if (data.topics && data.topics.includes(topic)) {
                    checkbox.checked = true;
                }
                label.appendChild(checkbox);
                label.appendChild(document.createTextNode(' ' + topic));
                topicsList.appendChild(label);
            });
            
            editModal.show();
        })
        .catch(error => {
            console.error('Error loading image:', error);
            alert('Error loading image details');
        });
}
''')
            continue
        
        # REPLACE: Update saveEdit to include accepted_answers
        if 'function saveEdit(event)' in line:
            output.append(line)
            # Skip old implementation
            bracket_count = 1
            i += 1
            while i < len(lines) and bracket_count > 0:
                if '{' in lines[i]:
                    bracket_count += lines[i].count('{')
                if '}' in lines[i]:
                    bracket_count -= lines[i].count('}')
                i += 1
            
            # Add new implementation
            output.append('''    event.preventDefault();
    const imageId = document.getElementById('edit_image_id').value;
    const formData = new FormData();
    formData.append('answer', document.getElementById('edit_answer').value);
    formData.append('hint', document.getElementById('edit_hint').value);
    formData.append('difficulty', document.getElementById('edit_difficulty').value);
    
    // NEW: Add accepted answers
    const acceptedAnswersText = document.getElementById('edit_accepted_answers').value.trim();
    if (acceptedAnswersText) {
        const variants = acceptedAnswersText.split('\\n')
            .map(v => v.trim())
            .filter(v => v.length > 0);
        formData.append('accepted_answers', JSON.stringify(variants));
    }
    
    const selectedTopics = Array.from(document.querySelectorAll('#edit_topics_list input:checked'))
        .map(cb => cb.value);
    selectedTopics.forEach(topic => formData.append('topics[]', topic));
    
    fetch(`/admin/who-am-i/edit/${imageId}`, {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            location.reload();
        } else {
            alert('Error: ' + (data.error || 'Failed to save changes'));
        }
    })
    .catch(error => {
        console.error('Error saving:', error);
        alert('Error saving changes');
    });
}
''')
            continue
        
        # Default: copy line as-is
        output.append(line)
        i += 1
    
    # Write output
    output_path = 'templates/admin_who_am_i.html.NEW'
    with open(output_path, 'w') as f:
        f.writelines(output)
    
    print(f"✓ Generated {output_path} ({len(output)} lines)")
    return output_path

if __name__ == '__main__':
    print("=" * 80)
    print("GENERATING COMPLETE WHO AM I FILES")
    print("=" * 80)
    print()
    
    if not os.path.exists('templates/admin_who_am_i.html'):
        print("❌ Error: Run this from /home/bbsisk/mathapp directory")
        sys.exit(1)
    
    try:
        template_path = generate_admin_template()
        
        print()
        print("=" * 80)
        print("FILES GENERATED SUCCESSFULLY")
        print("=" * 80)
        print()
        print("Generated files:")
        print(f"  1. {template_path}")
        print()
        print("To deploy:")
        print(f"  mv {template_path} templates/admin_who_am_i.html")
        print()
        print("⚠️  IMPORTANT: Also update app.py routes (see backend guide)")
        print()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
